from flask import Flask, render_template, request, redirect, session, flash 
from flask import request 
import mysql.connector 


hayvan = Flask(__name__, template_folder='templates_h') 
hayvan.secret_key = 'your_secret_key'


db = mysql.connector.connect( 
    host="localhost",
    user="root", 
    password="1234", 
    database="hayvan" 
)

cursor = db.cursor() 



@hayvan.route('/') 
def index():
    if 'user_id' not in session: 
        flash('Lütfen giriş yapın.', 'warning') 
        return redirect('/giris')  

    cursor.execute("SELECT * FROM hayvan_bilgileri WHERE sahiplenme_durumu = 'Sahiplenilmedi'")  
    hayvanlar = cursor.fetchall() 

    cursor.execute("SELECT * FROM hayvan_bilgileri WHERE sahiplenme_durumu = 'Sahiplenildi'")  
    sahiplenilenler = cursor.fetchall() 

    return render_template('index.html', hayvanlar=hayvanlar, sahiplenilenler=sahiplenilenler) 


@hayvan.route('/ekle', methods=['POST']) 
def hayvan_ekle():
    hayvan_turu = request.form['hayvan_turu'] 
    hayvan_saglik = request.form['hayvan_saglik']
    hayvan_yasi = request.form['hayvan_yasi'] 

    cursor.execute( 
        "INSERT INTO hayvan_bilgileri (hayvan_turu, hayvan_saglik, hayvan_yasi, sahiplenme_durumu) VALUES (%s, %s, %s, 'Sahiplenilmedi')",
        (hayvan_turu, hayvan_saglik, hayvan_yasi) 
    )
    db.commit()
    return redirect('/') 



@hayvan.route('/sil/<int:id>', methods=['POST']) 
def hayvan_sil(id):
    if request.form.get('_method') == 'DELETE': 
        cursor.execute("DELETE FROM hayvan_bilgileri WHERE id = %s", (id,)) 
        db.commit() 
    return redirect('/') 


@hayvan.route('/guncelle/<int:id>', methods=['POST']) 
def hayvan_guncelle(id):
    hayvan_turu = request.form['hayvan_turu']
    hayvan_saglik = request.form['hayvan_saglik']
    hayvan_yasi = request.form['hayvan_yasi']
    sahiplenme_durumu = request.form['sahiplenme_durumu']  

    cursor.execute( 
        "UPDATE hayvan_bilgileri SET hayvan_turu = %s, hayvan_saglik = %s, hayvan_yasi = %s, sahiplenme_durumu = %s WHERE id = %s",
        (hayvan_turu, hayvan_saglik, hayvan_yasi, sahiplenme_durumu, id) 
    )
    db.commit() 
    return redirect('/') 


@hayvan.route('/sahiplen/<int:id>', methods=['POST']) 
def hayvan_sahiplen(id):
    cursor.execute("UPDATE hayvan_bilgileri SET sahiplenme_durumu = 'Sahiplenildi' WHERE id = %s", (id,)) 
    db.commit() 
    flash('Hayvan sahiplenildi.', 'success')  
    return redirect('/') 

@hayvan.route('/kayit', methods=['GET', 'POST']) 
def kayit():
    if request.method == 'POST': 
        kullanici_adi = request.form['kullanici_adi'] 
        email = request.form['email'] 
        sifre = request.form['sifre'] 

        cursor.execute("SELECT * FROM kullanici WHERE email = %s", (email,))
        kullanici_var_mi = cursor.fetchone()
        if kullanici_var_mi:
            flash("❗ Bu e-posta adresi zaten kayıtlı!", "danger")
            return redirect('/kayit')
        cursor.execute("INSERT INTO kullanici (kullanici_adi, email, sifre) VALUES (%s, %s, %s)", (kullanici_adi, email, sifre)) 
        db.commit() 

        flash('✅ Kayıt başarılı, giriş yapabilirsiniz.', 'success')  
        return redirect('/giris')  

    return render_template('kayit.html')


@hayvan.route('/giris', methods=['GET', 'POST']) 
def giris():
    if request.method == 'POST': 
        email = request.form['email'] 
        sifre = request.form['sifre']

        cursor.execute("SELECT * FROM kullanici WHERE email = %s AND sifre = %s", (email, sifre)) 
        kullanici = cursor.fetchone() 

        if kullanici: 
            session['user_id'] = kullanici[0] 
            flash('Giriş başarılı.', 'success')  
            return redirect('/') 
        else:
            flash('Hatalı giriş bilgisi, lütfen tekrar deneyin.', 'danger')  
            return redirect('/giris') 

    return render_template('giris.html') 

if __name__ == '__main__': 
    hayvan.run(debug=True) 