package com.example.domain;

import java.util.Optional;

/** 請求書の保存先。実装は infrastructure 層に置く。 */
public interface InvoiceRepository {

    void save(Invoice invoice);

    Optional<Invoice> findById(String id);
}
