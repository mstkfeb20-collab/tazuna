package com.example.domain;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Objects;

/**
 * 金額。円単位の整数で保持する（INV-001）。
 * 金額は必ずこの型で受け渡し、double / float は使わない。
 */
public final class Money {

    private static final BigDecimal TAX_RATE = new BigDecimal("0.10");

    private final BigDecimal yen;

    private Money(BigDecimal yen) {
        if (yen.scale() > 0 && yen.stripTrailingZeros().scale() > 0) {
            throw new IllegalArgumentException("金額は1円単位で指定してください: " + yen);
        }
        if (yen.signum() < 0) {
            throw new IllegalArgumentException("金額は0円以上で指定してください: " + yen);
        }
        this.yen = yen.setScale(0, RoundingMode.UNNECESSARY);
    }

    public static Money yen(long yen) {
        return new Money(BigDecimal.valueOf(yen));
    }

    public static Money zero() {
        return yen(0);
    }

    public Money plus(Money other) {
        return new Money(this.yen.add(other.yen));
    }

    public Money times(int quantity) {
        if (quantity < 0) {
            throw new IllegalArgumentException("数量は0以上で指定してください: " + quantity);
        }
        return new Money(this.yen.multiply(BigDecimal.valueOf(quantity)));
    }

    /** 税込金額。1円未満は切り捨てる（REQ-001）。 */
    public Money withTax() {
        BigDecimal tax = this.yen.multiply(TAX_RATE).setScale(0, RoundingMode.DOWN);
        return new Money(this.yen.add(tax));
    }

    public long toLong() {
        return yen.longValueExact();
    }

    @Override
    public boolean equals(Object o) {
        return o instanceof Money other && yen.compareTo(other.yen) == 0;
    }

    @Override
    public int hashCode() {
        return Objects.hash(yen.stripTrailingZeros());
    }

    @Override
    public String toString() {
        return yen.toPlainString() + "円";
    }
}
