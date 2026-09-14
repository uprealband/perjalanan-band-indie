# UprealBand Photo Archive

Folder ini adalah arsip sumber foto perjalanan UprealBand.

## Struktur

`tahun/event/metadata.json + foto`

- Tahun = periode arsip.
- Folder event = konteks utama peristiwa.
- `metadata.json` = fakta, konteks, dan sumber bukti.
- Filename = identitas singkat foto dan petunjuk tambahan.

## Konvensi filename

Tanggal diketahui sampai hari:

`YYYY-MM-DD-event-slug-nama-orang.jpg`

Contoh:

`2009-05-30-pasar-seni-ancol-jon-bany-gerry.jpg`

Tanggal hanya diketahui bulan:

`YYYY-MM-event-slug-nomor.jpg`

Contoh:

`2013-06-pekan-raya-depok-01.jpg`

Tanggal hanya diketahui tahun:

`YYYY-event-slug-nama-orang.jpg`

Contoh:

`2012-unity-music-holic-jon-bany.jpg`

## Prinsip penting

1. Jangan menulis tanggal yang belum memiliki bukti.
2. Nama orang pada filename adalah petunjuk identitas, bukan otomatis hasil identifikasi visual.
3. Jika orang belum dapat dipastikan, jangan masukkan namanya hanya karena terlihat mirip.
4. Detail sejarah yang lebih lengkap masuk ke `metadata.json`.
5. Nama file dibuat ringkas karena folder sudah membawa konteks event.
6. Jangan menghapus foto lama hanya karena filename belum ideal. Perubahan nama harus mempertahankan blob/file yang sama.

## Status arsip lama

Foto yang masih memakai nama panjang atau nomor urut boleh dianggap sebagai legacy filename sampai dapat direnaming dengan aman. Metadata tidak boleh mengarang informasi yang tidak tersedia.

Tujuan akhirnya adalah agar arsip dapat dibaca manusia maupun mesin/AI sebagai kumpulan bukti sejarah yang saling terhubung, bukan sekadar galeri foto.
