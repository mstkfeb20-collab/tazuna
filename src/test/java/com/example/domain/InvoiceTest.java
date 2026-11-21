package com.example.domain;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

@Tag("REQ-002")
@DisplayName("REQ-002 請求書は 下書き→確定→支払済 の順にしか進まない")
class InvoiceTest {

    @Test
    @DisplayName("下書き→確定→支払済 の順に進められる")
    void forwardTransitions() {
        Invoice invoice = new Invoice("INV-1", Money.yen(1_000));
        invoice.issue();
        invoice.markPaid();
        assertEquals(Invoice.Status.PAID, invoice.status());
    }

    @Test
    @DisplayName("下書きから支払済には飛ばせない")
    void cannotSkipIssue() {
        Invoice invoice = new Invoice("INV-2", Money.yen(1_000));
        assertThrows(IllegalStateException.class, invoice::markPaid);
    }

    @Test
    @DisplayName("確定済みを再度確定できない")
    void cannotIssueTwice() {
        Invoice invoice = new Invoice("INV-3", Money.yen(1_000));
        invoice.issue();
        assertThrows(IllegalStateException.class, invoice::issue);
    }
}
