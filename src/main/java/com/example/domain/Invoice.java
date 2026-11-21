package com.example.domain;

import java.util.Objects;

/**
 * 請求書。状態は 下書き → 確定 → 支払済 の順にしか進まない（INV-002, REQ-002）。
 * 状態を直接書き換えるセッターは用意せず、遷移は専用メソッドだけで行う。
 */
public final class Invoice {

    public enum Status { DRAFT, ISSUED, PAID }

    private final String id;
    private final Money subtotal;
    private Status status;

    public Invoice(String id, Money subtotal) {
        this.id = Objects.requireNonNull(id);
        this.subtotal = Objects.requireNonNull(subtotal);
        this.status = Status.DRAFT;
    }

    public void issue() {
        transition(Status.DRAFT, Status.ISSUED);
    }

    public void markPaid() {
        transition(Status.ISSUED, Status.PAID);
    }

    private void transition(Status from, Status to) {
        if (status != from) {
            throw new IllegalStateException(
                "請求書 " + id + " は " + status + " のため " + to + " にできません（" + from + " からのみ遷移可能）");
        }
        status = to;
    }

    public Money totalWithTax() {
        return subtotal.withTax();
    }

    public String id() {
        return id;
    }

    public Status status() {
        return status;
    }
}
