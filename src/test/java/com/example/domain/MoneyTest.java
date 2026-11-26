package com.example.domain;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

@Tag("REQ-003")
@DisplayName("REQ-003 金額の計算（切り捨て・0円未満にしない）")
class MoneyTest {

    @Test
    @DisplayName("率を掛けた1円未満は切り捨てる")
    void percentRoundsDown() {
        assertEquals(Money.yen(3_333), Money.yen(11_111).percent(30));
    }

    @Test
    @DisplayName("返金額は0円を下回らない")
    void refundNeverNegative() {
        assertEquals(Money.zero(), Money.yen(1_000).minusOrZero(Money.yen(1_500)));
    }

    @Test
    @DisplayName("マイナスの金額は作れない")
    void noNegative() {
        assertThrows(IllegalArgumentException.class, () -> Money.yen(-1));
    }

    @Test
    @DisplayName("率は0〜100%。範囲の端は計算でき、外は計算しない")
    void percentRange() {
        assertEquals(Money.zero(), Money.yen(1_000).percent(0));
        assertEquals(Money.yen(1_000), Money.yen(1_000).percent(100));
        assertThrows(IllegalArgumentException.class, () -> Money.yen(1_000).percent(-1));
        assertThrows(IllegalArgumentException.class, () -> Money.yen(1_000).percent(101));
    }

    @Test
    @DisplayName("数量を掛けられるのは0以上")
    void timesRange() {
        assertEquals(Money.zero(), Money.yen(1_000).times(0));
        assertThrows(IllegalArgumentException.class, () -> Money.yen(1_000).times(-1));
    }
}
