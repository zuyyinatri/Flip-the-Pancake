# 🥞 Flip the Pancake

**Game Design Document**

Puzzle Game Berbasis Pygame

|---|---|
| **Nama Game** | Flip the Pancake |
| **Genre** | Puzzle |
| **Engine** | Pygame |
| **Bahasa Pemrograman** | Python |
---

## Daftar Isi

1. [Game Overview](#game-overview)
2. [Game Objectives](#game-objectives)
3. [Core Gameplay](#core-gameplay)
4. [Optimal Flip](#optimal-flip)
5. [Maximum Flip System](#maximum-flip-system)
6. [Level Design](#level-design)
7. [Scoring System](#scoring-system)
8. [Game Interface](#game-interface)
9. [Visual Design](#visual-design)
10. [Game States](#game-states)
11. [Difficulty Progression](#difficulty-progression)

---

## Game Overview

### Judul Game

*Flip the Pancake*

### Konsep Singkat

*Flip the Pancake* adalah permainan puzzle berbasis Pygame yang mengadaptasi konsep *pancake sorting*. Pemain diberikan sejumlah pancake dengan ukuran yang tersusun secara acak. Tujuan pemain adalah mengurutkan pancake sehingga pancake terbesar berada di bagian paling bawah dan pancake terkecil berada di bagian paling atas.

Pemain dapat memilih posisi tertentu pada tumpukan pancake untuk melakukan *flip*. Ketika sebuah posisi dipilih, seluruh pancake dari posisi tersebut hingga bagian paling atas akan dibalik urutannya.

Selain menyelesaikan puzzle, pemain dibatasi oleh jumlah maksimum *flip*. Batas tersebut ditentukan berdasarkan jumlah *flip* optimal yang diperlukan untuk menyelesaikan konfigurasi pancake.

---

## Game Objectives

Tujuan utama pemain adalah menyusun seluruh pancake berdasarkan ukuran. Urutan yang benar adalah:

> Pancake terkecil → pancake yang lebih besar → pancake terbesar

Dengan posisi pancake terbesar berada di bagian bawah tumpukan.

Sebagai contoh, jika terdapat pancake dengan ukuran:

```
[3, 1, 5, 2, 4]
```

maka kondisi akhir yang diharapkan adalah:

```
[1, 2, 3, 4, 5]
```

Pemain harus mencapai kondisi tersebut sebelum jumlah *flip* yang tersedia habis.

---

## Core Gameplay

### Pancake Stack

Setiap level memiliki sebuah tumpukan pancake dengan ukuran yang berbeda. Ukuran pancake direpresentasikan menggunakan bilangan bulat.

Contoh:

```
[4, 2, 5, 1, 3]
```

menunjukkan bahwa terdapat lima pancake dengan ukuran 1 sampai 5. Urutan pada awal permainan akan diacak.

### Flip Mechanic

Mekanisme utama permainan adalah membalik sebagian tumpukan pancake. Jika pemain memilih posisi `k`, maka seluruh pancake dari bagian atas hingga posisi tersebut akan dibalik.

Sebagai contoh:

```
[3, 1, 5, 2, 4]
```

Jika dilakukan *flip* pada tiga pancake pertama, maka hasilnya:

```
[5, 1, 3, 2, 4]
```

Operasi tersebut dapat dituliskan secara konseptual sebagai:

```
[a1, a2, ..., ak, ak+1, ..., an]
```

menjadi:

```
[ak, ak-1, ..., a1, ak+1, ..., an]
```

Setiap operasi *flip* akan mengurangi jumlah *flip* yang tersedia sebanyak satu.

### Win Condition

Pemain memenangkan level apabila seluruh pancake telah berada dalam urutan yang benar sebelum batas maksimum *flip* habis. Secara formal, kondisi kemenangan tercapai ketika:

```
P = [1, 2, 3, ..., n]
```

### Lose Condition

Pemain kalah apabila jumlah *flip* yang telah digunakan mencapai batas maksimum tetapi pancake belum berada dalam urutan yang benar.

---

## Optimal Flip

### Pengertian

Setiap konfigurasi pancake memiliki jumlah minimum operasi *flip* yang diperlukan untuk mencapai kondisi terurut. Jumlah tersebut disebut sebagai *optimal flip*.

Sebagai contoh, apabila suatu konfigurasi membutuhkan minimal tujuh operasi *flip*, maka:

```
Optimal Flip = 7
```

Nilai tersebut digunakan sebagai dasar untuk menentukan batas maksimum *flip* pada level.

### Pencarian Optimal Flip

Game akan menggunakan algoritma pencarian untuk memperoleh jumlah *flip* minimum.

Salah satu pendekatan yang digunakan adalah *Breadth-First Search* (BFS). Setiap konfigurasi pancake dianggap sebagai sebuah *state*, sedangkan operasi *flip* menghasilkan *state* baru.

Struktur pencarian secara umum adalah:

```
                 Initial State
                       |
          +------------+------------+
          |            |            |
       Flip 2       Flip 3       Flip 4
          |            |            |
        State        State        State
          |            |            |
         ...          ...          ...
                       |
                 Sorted State
```

BFS digunakan karena pencarian dilakukan berdasarkan jumlah operasi. State pertama yang mencapai kondisi terurut memiliki jumlah *flip* minimum.

---

## Maximum Flip System

### Konsep

Pemain tidak selalu diberikan jumlah *flip* yang sama dengan *optimal flip*. Pada level awal, pemain memperoleh beberapa *flip* tambahan sebagai toleransi.

Secara umum:

```
Maximum Flip = Optimal Flip + Bonus Flip
```

Bonus *flip* akan berkurang seiring meningkatnya level.

### Progresi Maximum Flip

Contoh rancangan progresi:

| Level | Bonus Flip | Maximum Flip |
|:---:|:---:|:---:|
| 1–3 | +5 | Optimal + 5 |
| 4–6 | +4 | Optimal + 4 |
| 7–9 | +3 | Optimal + 3 |
| 10–12 | +2 | Optimal + 2 |
| 13–15 | +1 | Optimal + 1 |
| 16+ | +0 | Optimal |

Nilai pada tabel merupakan rancangan awal dan dapat disesuaikan setelah dilakukan pengujian tingkat kesulitan. Dengan sistem ini, semakin tinggi level, pemain harus semakin dekat dengan solusi optimal.

---

## Level Design

### Peningkatan Jumlah Pancake

Jumlah pancake akan bertambah secara bertahap pada setiap level atau kelompok level.

Contoh rancangan:

| Level | Jumlah Pancake | Tujuan |
|:---:|:---:|---|
| 1–3 | 3 | Pengenalan mekanisme flip |
| 4–6 | 4 | Mulai meningkatkan kompleksitas |
| 7–9 | 5 | Pemain mulai membutuhkan perencanaan |
| 10–12 | 6 | Puzzle menjadi lebih kompleks |
| 13–15 | 7 | Membutuhkan strategi yang lebih baik |
| 16+ | 8+ | Tantangan tingkat lanjut |

Jumlah pancake dan jumlah level akhir dapat disesuaikan berdasarkan hasil pengujian performa algoritma serta tingkat kesulitan permainan.

### Level Generation

Pada awal setiap level, sistem akan:

1. Menentukan jumlah pancake.
2. Membuat pancake dengan ukuran unik.
3. Mengacak urutan pancake.
4. Menghitung *optimal flip*.
5. Menentukan *maximum flip*.
6. Menampilkan puzzle kepada pemain.

---

## Scoring System

Sistem skor dapat mempertimbangkan beberapa faktor:

- Jumlah *flip* yang digunakan.
- Jarak antara jumlah *flip* pemain dengan jumlah optimal.
- Waktu penyelesaian.
- Level yang berhasil diselesaikan.

Contoh konsep skor:

```
Efficiency = (Optimal Flip / Player Flip) × 100%
```

Semakin dekat jumlah *flip* pemain dengan jumlah optimal, semakin tinggi nilai efisiensinya. Sistem skor ini dapat digunakan sebagai fitur tambahan dan dapat dikembangkan setelah mekanisme utama permainan selesai.

---

## Game Interface

### Main Menu

Menu utama terdiri dari:

- Play
- How to Play
- Exit

### Gameplay Interface

Tampilan permainan setidaknya menampilkan:

- Tumpukan pancake.
- Nomor level.
- Jumlah *flip* yang telah digunakan.
- Jumlah maksimum *flip*.
- Tombol restart.

Contoh rancangan antarmuka:

```
+--------------------------------------+
|           FLIP THE PANCAKE           |
|                                      |
|  Level: 5             Flips: 4 / 10  |
|                                      |
|                 ______               |
|              _/________\_            |
|            _/____________\_          |
|          _/________________\_        |
|        _/____________________\_      |
|                                      |
|              [ RESTART ]             |
+--------------------------------------+
```

---

## Visual Design

### Pancake

Pancake direpresentasikan sebagai lingkaran pipih dengan ukuran yang berbeda. Ukuran visual pancake harus konsisten dengan nilai ukurannya.

Sebagai contoh:

- Ukuran 1: pancake paling kecil.
- Ukuran 2: sedikit lebih besar.
- ...
- Ukuran n: pancake paling besar.

### Animation

Animasi utama yang direncanakan adalah animasi ketika pancake dibalik berupa pergeseran posisi pancake. Animasi tambahan lain:

- Efek kemenangan.
- Efek ketika batas flip hampir habis.
- Transisi antarlevel.

---

## Game States

Game memiliki beberapa kondisi utama:

1. Main Menu
2. How to Play
3. Gameplay
4. Level Complete
5. Game Over
6. Victory

Perpindahan kondisi secara umum:

```
             Main Menu
                 |
                 v
             Gameplay
              /     \
             /       \
            v         v
     Level Complete  Game Over
            |
            v
       Next Level
            |
            v
        Gameplay
```

Jika seluruh level berhasil diselesaikan, pemain akan mencapai kondisi *Victory*.

---

## Difficulty Progression

Kesulitan game meningkat melalui dua mekanisme utama:

1. Penambahan jumlah pancake.
2. Pengurangan toleransi terhadap jumlah flip.

Pada level awal, pemain dapat menggunakan beberapa flip tambahan yang diberikan sistem.

Pada level yang lebih tinggi, jumlah maksimum flip semakin dekat dengan jumlah optimal. Dengan demikian, pemain tidak hanya dituntut untuk menyelesaikan puzzle, tetapi juga merencanakan urutan flip dengan efisien.

Konsep progresi dapat digambarkan sebagai:

```
Level Rendah
    |
    |  Banyak toleransi flip
    v
Level Menengah
    |
    |  Toleransi mulai berkurang
    v
Level Tinggi
    |
    |  Hampir/tidak ada toleransi
    v
Level Expert
```
