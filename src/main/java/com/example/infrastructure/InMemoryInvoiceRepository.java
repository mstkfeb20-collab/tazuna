package com.example.infrastructure;

import com.example.domain.Invoice;
import com.example.domain.InvoiceRepository;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

/** 見本用のインメモリ実装。案件では DB などの実装に置き換える。 */
public class InMemoryInvoiceRepository implements InvoiceRepository {

    private final Map<String, Invoice> store = new ConcurrentHashMap<>();

    @Override
    public void save(Invoice invoice) {
        store.put(invoice.id(), invoice);
    }

    @Override
    public Optional<Invoice> findById(String id) {
        return Optional.ofNullable(store.get(id));
    }
}
