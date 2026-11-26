package com.example.domain;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

@Tag("REQ-002")
@DisplayName("REQ-002 取消期限（業務ルールの層で確かめる）")
class CancellationPolicyTest {

    @Test
    @DisplayName("出発日の当日以降は取消料率を出さない（取り消せない）")
    void noRateOnDepartureDay() {
        assertThrows(IllegalArgumentException.class, () -> CancellationPolicy.rate(0));
        assertEquals(40, CancellationPolicy.rate(1));
    }
}
