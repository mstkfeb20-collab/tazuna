package com.example.domain;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

@Tag("REQ-001")
@DisplayName("REQ-001 予約の入力条件（業務ルールの層で確かめる）")
class ReservationInputTest {

    Tour tour(int seats) {
        return new Tour("T001", "春の京都 2日間", LocalDate.of(2027, 4, 30), Money.yen(30_000), Money.yen(15_000), seats);
    }

    @Test
    @DisplayName("人数にマイナスは指定できない（大人・子供とも）")
    void negativePeople() {
        assertThrows(IllegalArgumentException.class, () -> Reservation.create("R1", tour(10), -1, 2, ""));
        assertThrows(IllegalArgumentException.class, () -> Reservation.create("R1", tour(10), 2, -1, ""));
    }

    @Test
    @DisplayName("備考を省略すると空になる")
    void remarksOmitted() {
        assertEquals("", Reservation.create("R1", tour(10), 1, 0, null).remarks());
    }

    @Test
    @DisplayName("振込済の予約をもう一度振込済にはできない")
    void paidTwice() {
        Reservation r = Reservation.create("R1", tour(10), 1, 0, "");
        r.markPaid();
        assertThrows(IllegalStateException.class, r::markPaid);
        assertEquals(TransferStatus.PAID, r.status());
    }

    @Test
    @DisplayName("残席数にマイナスは指定できない")
    void negativeSeats() {
        assertThrows(IllegalArgumentException.class, () -> tour(-1));
        assertEquals(0, tour(0).remainingSeats());
    }

}
