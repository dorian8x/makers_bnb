from lib.booking import Booking

class BookingRepository:
    def __init__(self, connection):
        self._connection = connection

    def all(self):
        rows = self._connection.execute('SELECT * FROM bookings')

        bookings = []

        for row in rows:
            booking = Booking(row["id"], row["host_id"], row["guest_id"], row["space_id"], row["booking_date"], row["booking_status"])
            bookings.append(booking)

        return bookings

    def find(self, id):
        rows = self._connection.execute(
            'SELECT * FROM bookings WHERE id = %s', [id])
        row = rows[0]

        return Booking(row["id"], row["host_id"], row["guest_id"], row["space_id"], row["booking_date"], row["booking_status"])

    def create(self, booking):
        rows = self._connection.execute('INSERT INTO bookings (host_id, guest_id, space_id, booking_date, booking_status) VALUES (%s, %s, %s, %s, %s) RETURNING id', [
                                    booking.host_id, booking.guest_id, booking.space_id, booking.booking_date, booking.booking_status])
        row = rows[0]
        booking.id = row["id"]
        return booking

    def update(self, id, status):
        self._connection.execute('UPDATE bookings SET booking_status=%s WHERE id=%s', [status, id])
        return None

    def delete(self, id):
        self._connection.execute(
            'DELETE FROM bookings WHERE id = %s', [id])
        return None

    def find_by_guest_id(self, id):
        rows = self._connection.execute(
            'SELECT * FROM bookings WHERE guest_id = %s', [id])
        bookings = []

        for row in rows:
            booking = Booking(row["id"], row["host_id"], row["guest_id"], row["space_id"], row["booking_date"], row["booking_status"])
            bookings.append(booking)

        return bookings

    def find_by_host_id(self, id):
        rows = self._connection.execute(
            'SELECT * FROM bookings WHERE host_id = %s', [id])
        bookings = []

        for row in rows:
            booking = Booking(row["id"], row["host_id"], row["guest_id"], row["space_id"], row["booking_date"], row["booking_status"])
            bookings.append(booking)

        return bookings

    def find_by_space_id(self, space_id_to_find):
        query = self._connection.execute(
            "SELECT * FROM bookings WHERE space_id = %s",
            [space_id_to_find]
            )
        return [
            Booking(
                row["id"],
                row["host_id"],
                row["guest_id"],
                row["space_id"],
                row["booking_date"],
                row["booking_status"]
                )
            for row in query
            ]