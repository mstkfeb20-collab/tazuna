package com.example.domain;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

@Tag("REQ-001")
@DisplayName("REQ-001 請求金額は税込・1円単位で計算する")
class MoneyTest {

    @Test
    @DisplayName("税込金額の1円未満は切り捨てる")
    void withTaxRoundsDown() {
        assertEquals(Money.yen(1_100), Money.yen(1_000).withTax());
        assertEquals(Money.yen(108), Money.yen(99).withTax());
    }

    @Test
    @DisplayName("数量を掛けた金額を計算できる")
    void timesQuantity() {
        assertEquals(Money.yen(3_000), Money.yen(1_000).times(3));
    }

    @Test
    @DisplayName("負の金額は作れない")
    void rejectsNegative() {
        assertThrows(IllegalArgumentException.class, () -> Money.yen(-1));
    }
}
