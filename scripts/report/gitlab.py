"""GitLab の REST API を使う小さな道具（GitLab で運用する案件向け。標準ライブラリだけで動く）。

    python3 scripts/report/gitlab.py mr-body                      # 今の MR の説明を出す（CI の中で）
    python3 scripts/report/gitlab.py mr-note report.md            # MR にレポートを書く（同じメモを更新する）
    python3 scripts/report/gitlab.py issue-note "日次レポート（develop）" report.md   # その題の issue にメモを足す
    python3 scripts/report/gitlab.py transcribe-mr main body.md   # 転記の結果（作業ツリーの変更）をコミットし、転記の MR を出す

トークンは TAZUNA_GITLAB_TOKEN（なければ GITLAB_TOKEN）。プロジェクトのアクセストークン（ロールは Reporter 以上、
スコープは api。転記の MR を自動で出すときは Developer 以上）を、CI/CD の変数に「マスクする」で登録する。CI_JOB_TOKEN では MR へのメモが書けない。
社内の認証局の証明書を使う GitLab では、CI は Runner が渡す CI_SERVER_TLS_CA_FILE を、手元は TAZUNA_GITLAB_CA_FILE を読む。
GitLab の場所とプロジェクトは、CI では CI_API_V4_URL・CI_PROJECT_ID、手元では git の origin から決める。
案内役（next.py）も、ここの api() で MR・issue・パイプラインを読む。
"""
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

MARK = "<!-- tazuna:pr-report -->"


def token():
    return os.environ.get("TAZUNA_GITLAB_TOKEN") or os.environ.get("GITLAB_TOKEN") or ""


def _origin(root):
    try:
        return subprocess.run(["git", "-C", root, "remote", "get-url", "origin"],
                              capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def where(root="."):
    """(API の URL, プロジェクト)。わからなければ (None, None)"""
    if os.environ.get("CI_API_V4_URL") and os.environ.get("CI_PROJECT_ID"):
        return os.environ["CI_API_V4_URL"], os.environ["CI_PROJECT_ID"]
    url = _origin(root)
    # https://host/group/sub/project.git ・ git@host:group/project.git ・ ssh://git@host:2222/group/project.git
    m = re.match(r"(?:https?://(?:[^@/]+@)?([^/]+)/|ssh://(?:[^@/]+@)?([^/:]+)(?::\d+)?/|[^@]+@([^:]+):)(.+?)(?:\.git)?/?$", url)
    if not m:
        return None, None
    host = m.group(1) or m.group(2) or m.group(3)
    base = os.environ.get("TAZUNA_GITLAB_URL") or f"https://{host}"
    return base.rstrip("/") + "/api/v4", m.group(4)


def api(path, method="GET", data=None, root="."):
    """path は「projects/:id/…」のように書く。GET は全ページをまとめて返す。使えなければ None"""
    base, proj = where(root)
    if not base or not token():
        return None
    url = f"{base}/{path.replace(':id', urllib.parse.quote(str(proj), safe=''))}"
    ca = os.environ.get("TAZUNA_GITLAB_CA_FILE") or os.environ.get("CI_SERVER_TLS_CA_FILE")
    ctx = ssl.create_default_context(cafile=ca) if ca and os.path.isfile(ca) else None
    out = None
    while url:
        body = json.dumps(data).encode() if data is not None else None
        req = urllib.request.Request(url, data=body, method=method,
                                     headers={"PRIVATE-TOKEN": token(), "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
                got = json.loads(r.read() or b"null")
                nxt = r.headers.get("X-Next-Page") if method == "GET" else None
        except (urllib.error.URLError, OSError, ValueError):
            return None
        if isinstance(got, list):
            out = (out or []) + got
        else:
            return got
        if nxt:
            url = re.sub(r"([?&])page=\d+", "", url)
            url += ("&" if "?" in url else "?") + f"page={nxt}"
        else:
            url = None
    return out


def mr_body():
    """今の MR の説明。API で読めなければ、パイプラインを作った時点の CI_MERGE_REQUEST_DESCRIPTION"""
    iid = os.environ.get("CI_MERGE_REQUEST_IID")
    got = api(f"projects/:id/merge_requests/{iid}") if iid else None
    if isinstance(got, dict) and got.get("description") is not None:
        return got["description"]
    if os.environ.get("CI_MERGE_REQUEST_DESCRIPTION_IS_TRUNCATED") == "true":
        print("注意: MR の説明が長く、CI の変数では途中までしか読めません。TAZUNA_GITLAB_TOKEN を登録してください", file=sys.stderr)
    return os.environ.get("CI_MERGE_REQUEST_DESCRIPTION", "")


def mr_note(text):
    iid = os.environ.get("CI_MERGE_REQUEST_IID")
    if not iid:
        return "MR のパイプラインではありません"
    body = MARK + "\n" + text
    notes = api(f"projects/:id/merge_requests/{iid}/notes?per_page=100")
    if notes is None:
        return "GitLab に書けません（TAZUNA_GITLAB_TOKEN を確かめてください）"
    mine = next((n for n in notes if (n.get("body") or "").startswith(MARK)), None)
    if mine:
        ok = api(f"projects/:id/merge_requests/{iid}/notes/{mine['id']}", "PUT", {"body": body})
    else:
        ok = api(f"projects/:id/merge_requests/{iid}/notes", "POST", {"body": body})
    return None if ok is not None else "MR にメモを書けませんでした"


def issue_note(title, text, about=""):
    issues = api("projects/:id/issues?state=opened&per_page=100&search=" + urllib.parse.quote(title))
    if issues is None:
        return "GitLab に書けません（TAZUNA_GITLAB_TOKEN を確かめてください）"
    got = next((i for i in issues if i.get("title") == title), None)
    if not got:
        got = api("projects/:id/issues", "POST", {"title": title, "description": about})
        if not isinstance(got, dict):
            return "issue を作れませんでした"
    ok = api(f"projects/:id/issues/{got['iid']}/notes", "POST", {"body": text})
    return None if ok is not None else "issue にメモを書けませんでした"


def transcribe_mr(base, text, root="."):
    """作業ツリーの変更（転記の結果）を、base から作り直したブランチ tazuna/transcribe-<base> に1コミットで置き、
    転記の MR を出す（開いていれば説明を更新する）。git push は使わず API でコミットする"""
    out = subprocess.run(["git", "-C", root, "-c", "core.quotepath=false", "status", "--porcelain", "--untracked-files=all"],
                         capture_output=True, text=True).stdout
    actions = []
    for line in out.splitlines():
        st, path = line[:2], line[3:].strip().strip('"')
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if "D" in st:
            actions.append({"action": "delete", "file_path": path})
        else:
            with open(os.path.join(root, path), encoding="utf-8") as fp:
                actions.append({"action": "create" if st == "??" or "A" in st else "update",
                                "file_path": path, "content": fp.read()})
    if not actions:
        print("転記で変わるものはありません")
        return None
    br = "tazuna/transcribe-" + base.replace("/", "-")
    got = api("projects/:id/repository/commits", "POST", {
        "branch": br, "start_branch": base, "force": True,
        "commit_message": f"転記（{base} の設計書の変更から自動で作成）", "actions": actions}, root=root)
    if not isinstance(got, dict):
        return "転記のブランチにコミットできませんでした（トークンのロールが Developer 以上か確かめてください）"
    q = urllib.parse.quote
    mrs = api(f"projects/:id/merge_requests?state=opened&source_branch={q(br, safe='')}&target_branch={q(base, safe='')}", root=root)
    if mrs:
        ok = api(f"projects/:id/merge_requests/{mrs[0]['iid']}", "PUT", {"description": text}, root=root)
        print(f"転記の MR !{mrs[0]['iid']} を更新しました")
    else:
        ok = api("projects/:id/merge_requests", "POST", {"source_branch": br, "target_branch": base,
                                                          "title": f"転記: {base} の設計書の変更", "description": text,
                                                          "remove_source_branch": True}, root=root)
        print("転記の MR を出しました")
    return None if ok is not None else "転記の MR を出せませんでした"


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    cmd = sys.argv[1]
    if cmd == "mr-body":
        sys.stdout.write(mr_body())
        return 0
    if cmd == "mr-note" and len(sys.argv) == 3:
        err = mr_note(open(sys.argv[2], encoding="utf-8").read())
    elif cmd == "transcribe-mr" and len(sys.argv) == 4:
        err = transcribe_mr(sys.argv[2], open(sys.argv[3], encoding="utf-8").read(), os.environ.get("TAZUNA_ROOT", "."))
        if err:  # 転記の MR を出せなかったことは、ジョブを失敗にして気づけるようにする（手元で転記すれば代えられる）
            print("エラー: " + err + "。手元で python3 scripts/design/transcribe.py を実行して MR を出してください", file=sys.stderr)
            return 1
        return 0
    elif cmd == "issue-note" and len(sys.argv) in (4, 5):
        err = issue_note(sys.argv[2], open(sys.argv[3], encoding="utf-8").read(), sys.argv[4] if len(sys.argv) == 5 else "")
    else:
        print(__doc__, file=sys.stderr)
        return 2
    if err:
        # レポートは CI を止めない。書けなかったことだけ残す
        print("注意: " + err, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
