import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory,jsonify
from flask_mysqldb import MySQL,MySQLdb
import MySQLdb.cursors


app = Flask(__name__)

app.secret_key = 'kunci rahasia'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'inventarisgudang'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
@app.route('/kepsek', methods=['GET', 'POST'])
def loginkepsek():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'nip' in request.form:
        email = request.form['email']
        nip = request.form['nip']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM pegawai WHERE email = %s AND nip = %s', (email, nip,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id_user'] = account['id_user']
            session['email'] = account['email']
            return redirect(url_for('homekepsek'))
        else:
            msg = 'Nama Pengguna atau Kata Sandi Salah!'
    return render_template('loginkepalasekolah/loginkepsek.html', msg=msg)

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.route('/kepsek/homekepsek')
def homekepsek():
    if 'loggedin' in session:

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(*) AS jumlahbarang FROM masterbarang')
        jumlahbarang = cursor.fetchone()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(*) AS jumlahpermintaan FROM permintaan')
        jumlahpermintaan = cursor.fetchone()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(*) AS jumlahpegawai FROM pegawai')
        jumlahpegawai = cursor.fetchone()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(*) AS barangsedikit FROM masterbarang INNER JOIN stokbarang ON stokbarang.`id_stok` = masterbarang.`id_stok` WHERE stok < 3')
        barangsedikit = cursor.fetchone()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM pegawai INNER JOIN jabatan on jabatan.kode_jabatan = pegawai.kode_jabatan WHERE id_user = %s', (session['id_user'],))
        account = cursor.fetchone()
        return render_template('halamankepalasekolah/homekepsek.html', account=account, jumlahbarang=jumlahbarang, jumlahpermintaan=jumlahpermintaan, jumlahpegawai=jumlahpegawai,barangsedikit=barangsedikit)
    return redirect(url_for('loginkepsek'))

@app.route('/kepsek/homekepsek/profile')
def profilkepsek():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM pegawai INNER JOIN jabatan on jabatan.kode_jabatan = pegawai.kode_jabatan WHERE id_user = %s', (session['id_user'],))
        account = cursor.fetchone()
        return render_template('halamankepalasekolah/profilkepsek.html', account=account)
    return redirect(url_for('loginkepsek'))

@app.route('/img/<int:img_id>')
def serve_img(img_id):
    pass

@app.route('/kepsek/grafikkepsek')
def grafikkepsek():
    return render_template('halamankepalasekolah/grafik.html')

@app.route('/kepsek/logout')
def logoutkepsek():
   session.pop('loggedin', None)
   session.pop('id_user', None)
   session.pop('email', None)
   return redirect(url_for('loginkepsek'))

@app.route('/kepsek/listpermintaan')
def daftarpermintaan():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM permintaan INNER JOIN masterbarang on masterbarang.id_barang = permintaan.id_barang INNER JOIN jabatan on jabatan.kode_jabatan = permintaan.kode_jabatan INNER JOIN pegawai on pegawai.id_user = permintaan.id_user WHERE idstatuspesanan='1'")
    data = cur.fetchall()
    cur.close()
    return render_template('halamankepalasekolah/permintaan.html', permintaans=data)

@app.route('/kepsek/listpermintaan/accpermintaan/<string:id>', methods=['GET','POST'])
def accpermintaan(id):
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute('''
        UPDATE permintaan SET idstatuspesanan = '5' WHERE id_permintaan=%s''', (id, ))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('daftarpermintaan'))

    return render_template('halamankepalasekolah/permintaan.html')

@app.route('/kepsek/listpermintaan/tolakpermintaan/<string:id>', methods=['GET','POST'])
def tolakpermintaan(id):
    if request.method == 'GET':
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
        SELECT * FROM permintaan WHERE id_permintaan=%s''', (id, ))
        row = cursor.fetchone()
        cursor.close()

        return render_template('halamankepalasekolah/tolakpermintaan.html', row=row)
    else:
        alasan = request.form['alasan']

        cursor = mysql.connection.cursor()
        cursor.execute(''' 
        UPDATE permintaan 
        SET 
            idstatuspesanan = '4',
            alasan = %s
        WHERE
            id_permintaan = %s;
        ''',(alasan,id))
        
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('daftarpermintaan'))

# Batas Dari Halaman Kepala Sekolah #

@app.route('/kepgud', methods=['GET', 'POST'])
def loginkepgud():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'nip' in request.form:
        email = request.form['email']
        nip = request.form['nip']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM pegawai WHERE email = %s AND nip = %s', (email, nip,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id_user'] = account['id_user']
            session['email'] = account['email']
            return redirect(url_for('homekepgud'))
        else:
            msg = 'Nama Pengguna atau Kata Sandi Salah!'
    return render_template('loginkepalagudang/loginkepgud.html', msg=msg)

@app.route('/kepgud/homekepgud')
def homekepgud():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(*) AS jumlahbarang FROM masterbarang')
        jumlahbarang = cursor.fetchone()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(*) AS jumlahpermintaan FROM permintaan')
        jumlahpermintaan = cursor.fetchone()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(*) AS jumlahpegawai FROM pegawai')
        jumlahpegawai = cursor.fetchone()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(*) AS barangsedikit FROM masterbarang INNER JOIN stokbarang ON stokbarang.`id_stok` = masterbarang.`id_stok` WHERE stok < 3')
        barangsedikit = cursor.fetchone()

        return render_template('halamankepalagudang/homekepgud.html',jumlahbarang=jumlahbarang, jumlahpermintaan=jumlahpermintaan, jumlahpegawai=jumlahpegawai, barangsedikit=barangsedikit)
    return redirect(url_for('loginkepgud'))

@app.route('/kepgud/logout')
def logoutkepgud():
   session.pop('loggedin', None)
   session.pop('id_user', None)
   session.pop('email', None)
   return redirect(url_for('loginkepgud'))

@app.route('/kepgud/homekepgud/profile')
def profilkepgud():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM pegawai INNER JOIN jabatan on jabatan.kode_jabatan = pegawai.kode_jabatan WHERE id_user = %s', (session['id_user'],))
        account = cursor.fetchone()
        return render_template('halamankepalagudang/profilkepgud.html', account=account)
    return redirect(url_for('loginkepgud'))

@app.route('/kepgud/listpermintaan')
def listpermintaankepgud():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM permintaan INNER JOIN masterbarang on masterbarang.id_barang = permintaan.id_barang INNER JOIN jabatan on jabatan.kode_jabatan = permintaan.kode_jabatan INNER JOIN pegawai on pegawai.id_user = permintaan.id_user WHERE idstatuspesanan='5'")
    data = cur.fetchall()
    cur.close()
    return render_template('halamankepalagudang/permintaan.html', permintaans=data)

@app.route('/kepgud/daftarbarang')
def daftarbarang():

    cursor = mysql.connection.cursor()
    cursor.execute('select * from satuanbarang')
    satuanbarang = cursor.fetchall()
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute('select * from supplier')
    supplier = cursor.fetchall()
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute('select * from sumberdana')
    sumberdana = cursor.fetchall()
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute('select * from rak')
    rak = cursor.fetchall()
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM kategoribarang')
    kategoribarang = cursor.fetchall()
    cursor.close()

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM masterbarang LEFT JOIN stokbarang ON stokbarang.id_stok = masterbarang.id_stok LEFT JOIN rak ON rak.id_rak = stokbarang.id_rak LEFT JOIN sumberdana On sumberdana.idsumberdana = masterbarang.idsumberdana")
    data = cur.fetchall()
    cur.close()
    return render_template('halamankepalagudang/masterbarang.html', permintaans=data, kategoribarang=kategoribarang, rak=rak, satuanbarang=satuanbarang, supplier=supplier, sumberdana=sumberdana)

@app.route('/kepgud/daftarbarang/edit/<string:id>', methods=['GET', 'POST'])
def editmasterbarang(id):
    if request.method == 'GET':
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
        SELECT * FROM masterbarang INNER JOIN stokbarang ON stokbarang.`id_stok` = masterbarang.`id_stok` INNER JOIN kategoribarang ON kategoribarang.id_kategori = masterbarang.id_kategori INNER JOIN satuanbarang ON satuanbarang.id_satuan = masterbarang.id_satuan INNER JOIN sumberdana ON sumberdana.idsumberdana = masterbarang.idsumberdana WHERE id_barang=%s''', (id, ))
        row = cursor.fetchone()
        cursor.close()

        return render_template('halamankepalagudang/editmasterbarang.html', row=row)
    else:
        id_stok = request.form['id_stok']
        id_kategori = request.form['id_kategori']
        id_satuan = request.form['id_satuan']
        namabarang = request.form['namabarang']
        merk = request.form['merk']
        idsumberdana = request.form['idsumberdana']

        cursor = mysql.connection.cursor()
        cursor.execute(''' 
        UPDATE masterbarang 
        SET 
            id_stok = %s,
            id_kategori = %s,
            id_satuan = %s,
            namabarang = %s,
            merk = %s,
            idsumberdana = %s
        WHERE
            id_barang = %s;
        ''',(id_stok,id_kategori,id_satuan,namabarang,merk,idsumberdana,id))
        
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('daftarbarang'))

@app.route('/kepgud/daftarbarang/detailbarang/<string:id>', methods=['GET'])
def detailbarang(id):
    if request.method == 'GET':
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
        SELECT * FROM masterbarang INNER JOIN stokbarang ON stokbarang.`id_stok` = masterbarang.`id_stok` INNER JOIN kategoribarang ON kategoribarang.id_kategori = masterbarang.id_kategori INNER JOIN satuanbarang ON satuanbarang.id_satuan = masterbarang.id_satuan INNER JOIN sumberdana ON sumberdana.idsumberdana = masterbarang.idsumberdana INNER JOIN rak ON rak.id_rak = stokbarang.id_rak WHERE id_barang=%s''', (id, ))
        row = cursor.fetchone()
        cursor.close()

        return render_template('halamankepalagudang/detailbarang.html', row=row)

@app.route('/kepgud/daftarbarang/hapusbarang/<string:id>', methods=['GET'])
def hapusbarang(id):
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute('''
        DELETE 
        FROM masterbarang 
        WHERE id_barang=%s''', (id, ))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('daftarbarang'))

    return render_template('halamankepalagudang/daftarbarang.html')

@app.route('/kepgud/daftarbarang/tambahbarang', methods=['GET', 'POST'])
def tambahbarang():
    if request.method == 'GET':
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM kategoribarang')
        row = cursor.fetchall()
        cursor.close()

        cursor = mysql.connection.cursor()
        cursor.execute('select * from satuanbarang')
        satuanbarang = cursor.fetchall()
        cursor.close()

        cursor = mysql.connection.cursor()
        cursor.execute('select * from supplier')
        supplier = cursor.fetchall()
        cursor.close()

        cursor = mysql.connection.cursor()
        cursor.execute('select * from sumberdana')
        sumberdana = cursor.fetchall()
        cursor.close()

        cursor = mysql.connection.cursor()
        cursor.execute('select * from rak')
        rak = cursor.fetchall()
        cursor.close()

        return render_template('halamankepalagudang/masterbarang.html', daftarbarang=row, sumberdana=sumberdana, satuanbarang=satuanbarang, rak=rak, supplier=supplier)
    else:

        stok = request.form['stok']
        jml_barang_msk = request.form['jml_barang_msk']
        hrg_satuan = request.form['hrg_satuan']
        total = request.form['total']
        id_supplier = request.form['id_supplier']
        id_rak = request.form['id_rak']

        id_barang = request.form['id_barang']
        id_stok = request.form['id_stok']
        id_kategori = request.form['id_kategori']
        id_satuan = request.form['id_satuan']
        namabarang = request.form['namabarang']
        merk = request.form['merk']
        idsumberdana = request.form['idsumberdana']
        
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO stokbarang(id_stok,stok,jml_barang_msk,tgl_masuk,hrg_satuan,total,id_supplier,id_rak) VALUES(%s,%s,%s,NOW(),%s,%s,%s,%s)',(id_stok, stok, jml_barang_msk, hrg_satuan, total, id_supplier, id_rak))
        cursor.execute('INSERT INTO masterbarang(id_barang, id_stok, id_kategori, id_satuan, namabarang, merk, idsumberdana) VALUES(%s,%s,%s,%s,%s,%s,%s)',(id_barang, id_stok, id_kategori, id_satuan, namabarang, merk , idsumberdana))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('daftarbarang'))

@app.route('/kepgud/listpermintaan/barangsiap/<string:id>', methods=['GET','POST'])
def barangsiap(id):
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute('''
        UPDATE permintaan SET idstatuspesanan = '2' WHERE id_permintaan=%s''', (id, ))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('listpermintaankepgud'))

    return render_template('halamankepalagudang/permintaan.html')

@app.route('/kepgud/barangkeluar')
def barangkeluar():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM barangkeluar')
    row = cursor.fetchall()
    cursor.close()

    return render_template('halamankepalagudang/barangkeluar.html', databarangkeluar=row)

@app.route('/kepgud/datasupplier')
def datasupplier():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM supplier')
    row = cursor.fetchall()
    cursor.close()

    return render_template('halamankepalagudang/supplier.html', datasupplier=row)

@app.route('/kepgud/datasupplier/tambahsupplier', methods=['GET', 'POST'])
def tambahsupplier():
    if request.method == 'GET':
        return render_template('halamankepalagudang/tambahsupplier.html')
    else:
        id_supplier = request.form['id_supplier']
        namasupplier = request.form['namasupplier']
        nomortelepon = request.form['nomortelepon']
        email = request.form['email']
        alamat = request.form['alamat']
      
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO supplier(id_supplier,namasupplier, nomortelepon, email, alamat) VALUES(%s,%s,%s,%s,%s)''',(id_supplier,namasupplier,nomortelepon,email,alamat))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('datasupplier'))

@app.route('/kepgud/datasupplier/editsupplier/<string:id>', methods=['GET', 'POST'])
def editsupplier(id):
    if request.method == 'GET':
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
        SELECT * 
        FROM supplier 
        WHERE id_supplier=%s''', (id, ))
        row = cursor.fetchone()
        cursor.close()

        return render_template('halamankepalagudang/editsupplier.html', row=row)
    else:
        namasupplier = request.form['namasupplier']
        nomortelepon = request.form['nomortelepon']
        email = request.form['email']
        alamat = request.form['alamat']

        cursor = mysql.connection.cursor()
        cursor.execute(''' 
        UPDATE supplier 
        SET 
            namasupplier = %s,
            nomortelepon = %s,
            email = %s,
            alamat = %s
        WHERE
            id_supplier = %s;
        ''',(namasupplier, nomortelepon, email, alamat,id))
        
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('datasupplier'))

@app.route('/kepgud/datasupplier/hapussupplier/<string:id>', methods=['GET'])
def hapussupplier(id):
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute('''
        DELETE FROM supplier WHERE id_supplier=%s''', (id, ))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('datasupplier'))

    return render_template('halamankepalagudang/supplier.html')


@app.route('/kepgud/sumberdana')
def sumberdana():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM sumberdana')
    row = cursor.fetchall()
    cursor.close()

    return render_template('halamankepalagudang/sumberdana.html', sumberdana=row)

@app.route('/kepgud/sumberdana/tambahsumberdana', methods=['GET', 'POST'])
def tambahsumberdana():
    if request.method == 'GET':
        return render_template('halamankepalagudang/tambahsumberdana.html')
    else:
        idsumberdana = request.form['idsumberdana']
        namasumberdana = request.form['namasumberdana']
      
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO sumberdana(idsumberdana,namasumberdana) VALUES(%s,%s)''',(idsumberdana,namasumberdana))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('sumberdana'))

@app.route('/kepgud/sumberdana/editsumberdana/<string:id>', methods=['GET', 'POST'])
def editsumberdana(id):
    if request.method == 'GET':
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
        SELECT * 
        FROM sumberdana 
        WHERE idsumberdana=%s''', (id, ))
        row = cursor.fetchone()
        cursor.close()

        return render_template('halamankepalagudang/editsumberdana.html', row=row)
    else:
        namasumberdana = request.form['namasumberdana']

        cursor = mysql.connection.cursor()
        cursor.execute(''' 
        UPDATE sumberdana 
        SET 
            namasumberdana = %s
        WHERE
            idsumberdana = %s;
        ''',(namasumberdana,id))
        
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('sumberdana'))

@app.route('/kepgud/sumberdana/hapussumberdana/<string:id>', methods=['GET'])
def hapussumberdana(id):
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute('''
        DELETE FROM sumberdana WHERE idsumberdana=%s''', (id, ))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('sumberdana'))

    return render_template('halamankepalagudang/sumberdana.html')

@app.route('/kepgud/rakbarang')
def rakbarang():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM rak')
    row = cursor.fetchall()
    cursor.close()

    return render_template('halamankepalagudang/rak.html', rakbarang=row)

@app.route('/kepgud/rakbarang/tambahrakbarang', methods=['GET', 'POST'])
def tambahrakbarang():
    if request.method == 'GET':
        return render_template('halamankepalagudang/tambahrakbarang.html')
    else:
        id_rak = request.form['id_rak']
        nama_rak = request.form['nama_rak']
        kapasitas_rak = request.form['kapasitas_rak']
      
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO rak(id_rak,nama_rak,kapasitas_rak) VALUES(%s,%s,%s)''',(id_rak,nama_rak,kapasitas_rak))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('rakbarang'))

@app.route('/kepgud/rakbarang/editrak/<string:id>', methods=['GET', 'POST'])
def editrak(id):
    if request.method == 'GET':
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
        SELECT * 
        FROM rak 
        WHERE id_rak=%s''', (id, ))
        row = cursor.fetchone()
        cursor.close()

        return render_template('halamankepalagudang/editrak.html', row=row)
    else:
        nama_rak = request.form['nama_rak']
        kapasitas_rak = request.form['kapasitas_rak']

        cursor = mysql.connection.cursor()
        cursor.execute(''' 
        UPDATE rak 
        SET 
            nama_rak = %s,
            kapasitas_rak = %s
        WHERE
            id_rak = %s;
        ''',(nama_rak, kapasitas_rak,id))
        
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('rakbarang'))

@app.route('/kepgud/rakbarang/hapusrak/<string:id>', methods=['GET'])
def hapusrak(id):
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute('''
        DELETE FROM rak WHERE id_rak=%s''', (id, ))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('rakbarang'))

    return render_template('halamankepalagudang/rak.html')

@app.route('/kepgud/kategoribarang')
def kategoribarang():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM kategoribarang')
    row = cursor.fetchall()
    cursor.close()

    return render_template('halamankepalagudang/kategoribarang.html', kategoribarang=row)

@app.route('/kepgud/kategoribarang/tambahkategoribarang', methods=['POST'])
def tambahkategoribarang():
    id_kategori = request.form['id_kategori']
    namakategori = request.form['namakategori']
      
    cursor = mysql.connection.cursor()
    cursor.execute('''INSERT INTO kategoribarang(id_kategori,namakategori) VALUES(%s,%s)''',(id_kategori,namakategori))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('kategoribarang'))

@app.route('/kepgud/kategoribarang/editkategori/<string:id>', methods=['GET', 'POST'])
def editkategori(id):
    if request.method == 'GET':
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
        SELECT * 
        FROM kategoribarang 
        WHERE id_kategori=%s''', (id, ))
        row = cursor.fetchone()
        cursor.close()

        return render_template('halamankepalagudang/editkategoribarang.html', row=row)
    else:
        namakategori = request.form['namakategori']

        cursor = mysql.connection.cursor()
        cursor.execute(''' 
        UPDATE kategoribarang 
        SET 
            namakategori = %s
        WHERE
            id_kategori = %s;
        ''',(namakategori,id))
        
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('kategoribarang'))

@app.route('/kepgud/kategoribarang/hapuskategori/<int:id>', methods=['GET'])
def hapuskategori(id):
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute('''
        DELETE FROM kategoribarang WHERE id_kategori=%s''', (id, ))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('kategoribarang'))

    return render_template('halamankepalagudang/kategoribarang.html')

@app.route('/kepgud/satuanbarang')
def satuanbarang():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM satuanbarang')
    row = cursor.fetchall()
    cursor.close()

    return render_template('halamankepalagudang/satuanbarang.html', satuanbarang=row)

@app.route('/kepgud/satuanbarang/tambahsatuanbarang', methods=['GET', 'POST'])
def tambahsatuanbarang():
    if request.method == 'GET':
        return render_template('halamankepalagudang/tambahsatuanbarang.html')
    else:
        id_satuan = request.form['id_satuan']
        nama_satuan = request.form['nama_satuan']
      
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO satuanbarang(id_satuan,nama_satuan) VALUES(%s,%s)''',(id_satuan,nama_satuan))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('satuanbarang'))

@app.route('/kepgud/satuanbarang/editsatuan/<string:id>', methods=['GET', 'POST'])
def editsatuan(id):
    if request.method == 'GET':
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
        SELECT * 
        FROM satuanbarang 
        WHERE id_satuan=%s''', (id, ))
        row = cursor.fetchone()
        cursor.close()

        return render_template('halamankepalagudang/editsatuan.html', row=row)
    else:
        nama_satuan = request.form['nama_satuan']

        cursor = mysql.connection.cursor()
        cursor.execute(''' 
        UPDATE satuanbarang 
        SET 
            nama_satuan = %s
        WHERE
            id_satuan = %s;
        ''',(nama_satuan,id))
        
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('satuanbarang'))

@app.route('/kepgud/satuanbarang/hapussatuan/<string:id>', methods=['GET'])
def hapussatuan(id):
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute('''
        DELETE 
        FROM satuanbarang 
        WHERE id_satuan=%s''', (id, ))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('satuanbarang'))

    return render_template('halamankepalagudang/satuanbarang.html')

@app.route('/kepgud/stokbarang')
def stokbarang():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM stokbarang LEFT JOIN masterbarang ON masterbarang.id_stok = stokbarang.id_stok')
    row = cursor.fetchall()
    cursor.close()

    return render_template('halamankepalagudang/stokbarang.html', stokbarang=row)

@app.route('/kepgud/unitkerja')
def unitkerja():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM unitkerja')
    row = cursor.fetchall()
    cursor.close()

    return render_template('halamankepalagudang/unitkerja.html', unitkerja=row)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/kepgud/unitkerja/tambahunitkerja', methods=['GET', 'POST'])
def tambahunitkerja():
    if request.method == 'GET':
        return render_template('halamankepalagudang/tambahstatus.html')
    else:
        id_unitkerja = request.form['id_unitkerja']
        nama = request.form['nama']
        alamat = request.form['alamat']
        no_telp = request.form['no_telp']
        no_fax = request.form['no_fax']
        email = request.form['email']
        web = request.form['web']
        cabang = request.form['cabang']
      
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO unitkerja(id_unitkerja, nama, alamat, no_telp, no_fax, email, web, cabang) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)''',(id_unitkerja, nama, alamat, no_telp, no_fax, email, web, cabang))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('unitkerja'))

@app.route('/kepgud/daftarstatus')
def daftarstatus():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM status')
    row = cursor.fetchall()
    cursor.close()

    return render_template('halamankepalagudang/daftarstatus.html', daftarstatus=row)

@app.route('/kepgud/daftarstatus/tambahstatus', methods=['GET', 'POST'])
def tambahstatus():
    if request.method == 'GET':
        return render_template('halamankepalagudang/tambahstatus.html')
    else:
        id_status = request.form['id_status']
        nama_status = request.form['nama_status']
      
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO status(id_status,nama_status) VALUES(%s,%s)''',(id_status,nama_status))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('daftarstatus'))

@app.route('/kepgud/daftarstatus/editstatus/<string:id>', methods=['GET', 'POST'])
def editstatus(id):
    if request.method == 'GET':
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
        SELECT * 
        FROM status 
        WHERE id_status=%s''', (id, ))
        row = cursor.fetchone()
        cursor.close()

        return render_template('halamankepalagudang/editstatus.html', row=row)
    else:
        nama_status = request.form['nama_status']

        cursor = mysql.connection.cursor()
        cursor.execute(''' 
        UPDATE status 
        SET 
            nama_status = %s
        WHERE
            id_status = %s;
        ''',(nama_status,id))
        
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('daftarstatus'))

@app.route('/kepgud/daftarstatus/hapusstatus/<string:id>', methods=['GET'])
def hapusstatus(id):
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute('''
        DELETE 
        FROM status WHERE id_status=%s''', (id, ))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('daftarstatus'))

    return render_template('halamankepalagudang/daftarstatus.html')

@app.route('/kepgud/daftarjabatan')
def daftarjabatan():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM jabatan')
    row = cursor.fetchall()
    cursor.close()

    return render_template('halamankepalagudang/daftarjabatan.html', daftarjabatan=row)

@app.route('/kepgud/daftarjabatan/tambahjabatan', methods=['GET', 'POST'])
def tambahjabatan():
    if request.method == 'GET':
        return render_template('halamankepalagudang/tambahjabatan.html')
    else:
        kode_jabatan = request.form['kode_jabatan']
        nama_jabatan = request.form['nama_jabatan']
      
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO jabatan(kode_jabatan,nama_jabatan) VALUES(%s,%s)''',(kode_jabatan,nama_jabatan))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('daftarjabatan'))

@app.route('/kepgud/daftarjabatan/editjabatan/<string:id>', methods=['GET', 'POST'])
def editjabatan(id):
    if request.method == 'GET':
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
        SELECT * 
        FROM jabatan 
        WHERE kode_jabatan=%s''', (id, ))
        row = cursor.fetchone()
        cursor.close()

        return render_template('halamankepalagudang/editjabatan.html', row=row)
    else:
        nama_jabatan = request.form['nama_jabatan']

        cursor = mysql.connection.cursor()
        cursor.execute(''' 
        UPDATE jabatan 
        SET 
            nama_jabatan = %s
        WHERE
            kode_jabatan = %s;
        ''',(nama_jabatan,id))
        
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('daftarjabatan'))

@app.route('/kepgud/daftarjabatan/hapusjabatan/<string:id>', methods=['GET'])
def hapusjabatan(id):
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute('''
        DELETE 
        FROM jabatan WHERE kode_jabatan=%s''', (id, ))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('daftarjabatan'))

    return render_template('halamankepalagudang/daftarjabatan.html')

@app.route('/kepgud/grafik')
def grafik():
    return render_template('halamankepalagudang/grafik.html')

# Batas halaman kepala gudang #

@app.route('/pegawai', methods=['GET', 'POST'])
def loginpegawai():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'nip' in request.form:
        email = request.form['email']
        nip = request.form['nip']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM pegawai INNER JOIN jabatan ON jabatan.`kode_jabatan`=pegawai.`kode_jabatan` WHERE email = %s AND nip = %s', (email, nip,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id_user'] = account['id_user']
            session['email'] = account['email']
            return redirect(url_for('homepegawai'))
        else:
            msg = 'Nama Pengguna atau Kata Sandi Salah!'
    return render_template('loginpegawai/loginpegawai.html', msg=msg)

@app.route('/pegawai/homepegawai')
def homepegawai():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM pegawai INNER JOIN jabatan on jabatan.kode_jabatan = pegawai.kode_jabatan LEFT JOIN permintaan ON permintaan.id_user = pegawai.id_user WHERE pegawai.id_user = %s', (session['id_user'],))
        account = cursor.fetchone()
        return render_template('halamanpegawai/homepegawai.html', account=account)
    return redirect(url_for('loginpegawai'))

@app.route('/pegawai/logout')
def logoutpegawai():
   session.pop('loggedin', None)
   session.pop('id_user', None)
   session.pop('email', None)
   session.pop('kode_jabatan', None)
   return redirect(url_for('loginpegawai'))

@app.route('/pegawai/homepegawai/profile')
def profilpegawai():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM pegawai INNER JOIN jabatan on jabatan.kode_jabatan = pegawai.kode_jabatan LEFT JOIN permintaan ON permintaan.id_user = pegawai.id_user WHERE pegawai.id_user = %s', (session['id_user'],))
        account = cursor.fetchone()
        return render_template('halamanpegawai/profilpegawai.html', account=account)
    return redirect(url_for('loginpegawai'))

@app.route('/pegawai/homepegawai/listpermintaan')
def listpesanan():
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM permintaan INNER JOIN masterbarang on masterbarang.id_barang = permintaan.id_barang INNER JOIN jabatan on jabatan.kode_jabatan = permintaan.kode_jabatan INNER JOIN pegawai on pegawai.id_user = permintaan.id_user INNER JOIN statuspesanan ON statuspesanan.idstatuspesanan = permintaan.idstatuspesanan WHERE permintaan.id_user = %s", (session['id_user'],))
        account = cur.fetchall()
        cur.close()
        return render_template('halamanpegawai/permintaan.html', account=account)
    return redirect(url_for('loginpegawai'))

@app.route('/register',methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM jabatan')
        row = cursor.fetchall()
        cursor.close()

        return render_template('register.html', row=row)
    else:
        id_user = request.form['id_user']
        kode_jabatan = request.form['kode_jabatan']
        nama = request.form['nama']
        nip = request.form['nip']
        email = request.form['email']
        nomor_tlp = request.form['nomor_tlp']

        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO pegawai(id_user, kode_jabatan, nama, nip, email, id_status, nomor_tlp) VALUES(%s,%s,%s,%s,%s,'S1',%s)''',(id_user, kode_jabatan, nama, nip, email, nomor_tlp))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('register'))
    
@app.route('/pegawai/homepegawai/buatpermintaan')
def buatpermintaan():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM masterbarang LEFT JOIN stokbarang ON stokbarang.`id_stok` = masterbarang.`id_stok` LEFT JOIN satuanbarang ON satuanbarang.`id_satuan` = masterbarang.`id_satuan` LEFT JOIN sumberdana ON sumberdana.idsumberdana = masterbarang.idsumberdana')
    data = cur.fetchall()
    cur.close()
    return render_template('halamanpegawai/buatpermintaan.html', daftarbarang=data)

@app.route('/pegawai/homepegawai/buatpermintaan/orderbarang/<string:id>', methods=['GET', 'POST'])
def orderbarang(id):
    if request.method=='GET':

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM pegawai INNER JOIN jabatan on jabatan.kode_jabatan = pegawai.kode_jabatan LEFT JOIN permintaan ON permintaan.id_user = pegawai.id_user WHERE pegawai.id_user = %s', (session['id_user'],))
        account = cursor.fetchone()

        cursor = mysql.connection.cursor()
        cursor.execute (''' SELECT * FROM masterbarang LEFT JOIN permintaan ON permintaan.`id_barang`= masterbarang.`id_barang` LEFT JOIN pegawai ON pegawai.`id_user`=permintaan.`id_user` LEFT JOIN jabatan ON jabatan.kode_jabatan = pegawai.kode_jabatan WHERE masterbarang.id_barang=%s''', (id, ))
        row = cursor.fetchone()
        cursor.close()
        return render_template('halamanpegawai/orderbarang.html', row=row,account=account)

    elif 'loggedin' in session:
        id_permintaan = request.form['id_permintaan']
        id_unitkerja = request.form['id_unitkerja']
        id_user = request.form['id_user']
        kode_jabatan = request.form['kode_jabatan']
        id_barang = request.form['id_barang']
        jumlahpesan = request.form['jumlahpesan']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''INSERT INTO permintaan(id_permintaan, id_unitkerja, id_user, kode_jabatan, id_barang, jumlahpesan, tanggalpesan, idstatuspesanan) VALUES (%s, %s, %s, %s, %s, %s, NOW(), '1') ''',(id_permintaan, id_unitkerja, id_user, kode_jabatan, id_barang, jumlahpesan,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('listpesanan'))



if __name__ == '__main__':
    app.run(debug=True)