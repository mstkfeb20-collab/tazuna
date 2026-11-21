package com.example.application;

import com.example.domain.Invoice;
import com.example.domain.InvoiceRepository;
import com.example.domain.Money;

/** 請求書のユースケース。domain だけに依存する。 */
public class InvoiceService {

    private final InvoiceRepository repository;

    public InvoiceService(InvoiceRepository repository) {
        this.repository = repository;
    }

    public Invoice createDraft(String id, Money unitPrice, int quantity) {
        Invoice invoice = new Invoice(id, unitPrice.times(quantity));
        repository.save(invoice);
        return invoice;
    }

    public Invoice issue(String id) {
        Invoice invoice = find(id);
        invoice.issue();
        repository.save(invoice);
        return invoice;
    }

    public Invoice pay(String id) {
        Invoice invoice = find(id);
        invoice.markPaid();
        repository.save(invoice);
        return invoice;
    }

    private Invoice find(String id) {
        return repository.findById(id)
            .orElseThrow(() -> new IllegalArgumentException("請求書が見つかりません: " + id));
    }
}
