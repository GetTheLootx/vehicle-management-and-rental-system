from time import strftime
from urllib import response
from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify, make_response
from flask_login import login_required, current_user
from .models import User, customer, pujceno, trailer, back
from . import db, mail
from datetime import datetime, timedelta, time
import pdfkit
import math
from flask_mail import Mail, Message

views = Blueprint('views', __name__)


@views.route("/home")
@views.route("/")
@login_required
def home():
    if current_user.name == "admin":
        isTrailer = trailer.query.all()
        # isCategory = category.query.all()
        return render_template("home.html", user=current_user, trailer=isTrailer, date=datetime.now())
    else:
        return redirect(url_for('auth.login'))


# Hlavní formulář, který má na starost odbavení přívěsného vozíku. Script nejdříve zkontroluje zda je uživatel přihlášen jako admin a poté postupuje dle podmínek.
# Zkontrolují se správnost vstupu. Pokud v databazi není uveden zákazníík pod svým ID (občanský průkaz) kod ho uloží do databáze.
# Při znovu pronájmu daného vozíku se zkontroluje zda není zákazník již uložen, pokud ano, vybere se zákazník podle ID karty,
# získá se ID zákazníka a poté se záznam uloží do tabulky "pujceno", která zaznamenává ID vozíku, ID zákazníka, vytvoří se datumy a zaznamená celková cena pronájmu

@views.route("/formular", methods=['POST', 'GET'])
@login_required
def formular():
    if current_user.name == "admin":
        customers = customer.query.all()
        trailers = trailer.query.all()
        pujcen = pujceno.query.order_by(pujceno.date_back.desc()).all()

        if not trailers:
            flash('Nejdříve přidejte vodzidlo', category="error")
            return redirect(url_for('views.add_trailer'))

        trailers = trailer.query.all()
        if request.method == 'POST':
            id_card = request.form.get("id_card")
            firstname = request.form.get("firstname")
            lastname = request.form.get("lastname")
            bydliste = request.form.get("bydliste")
            phone = request.form.get("phone")
            vehicle = request.form.get("trailer")
            gdpr = request.form.get("gdpr")
            contract = request.form.get("contract")
            #price = int(request.form.get("price"))

            if gdpr and contract:
                gdpr = True
                contract = True

            dateStart = request.form.get("startDate")
            when_back = request.form.get("when_back")

            dateStart = datetime.strptime(dateStart, "%d. %m. %Y %H:%M")
            when_back = datetime.strptime(when_back, "%d. %m. %Y %H:%M")

            totalDays = math.ceil(
                ((when_back - dateStart).total_seconds())/86400)

            if not vehicle:
                flash("Žádné vozidlo vybráno", category="error")
                return redirect(url_for('views.formular'))

            else:
                isCustomer = customer.query.filter_by(id_card=id_card).first()
                isTrailer = trailer.query.filter_by(spz=vehicle).first()

                trailerId = isTrailer.id
                trailerPrice = isTrailer.price

                if totalDays < 1:
                    TotalPrice = (totalDays + 1) * trailerPrice
                else:
                    TotalPrice = totalDays * trailerPrice

                # isPujceno = pujceno.query.filter_by(trailer_id=trailerId)

                # for pujcen in isPujceno:
                #     date_back = pujcen.date_back
                #     when_back = pujcen.when_back
                #     date_created = pujcen.date_created

                #     # if date_back:
                #     #     totalDays_back = math.ceil(
                #     #         ((date_back - date_created).total_seconds())/86400)

                if not id_card and not isCustomer:
                    flash("Vyplňte číslo občanského průkazu", category="error")
                    return redirect(url_for('views.formular'))
                elif not firstname and not isCustomer:
                    flash("Vyplňte jméno", category="error")
                    return redirect(url_for('views.formular'))
                elif not id_card and not isCustomer:
                    flash("Vyplňte 6 posledních číslich občanského průkazu",
                          category="error")
                    return redirect(url_for('views.formular'))
                elif not lastname and not isCustomer:
                    flash("Vyplňte příjmení", category="error")
                    return redirect(url_for('views.formular'))
                elif not bydliste and not isCustomer:
                    flash("Vyplňte adresu", category="error")
                    return redirect(url_for('views.formular'))
                elif not phone and not isCustomer:
                    flash("Vyplňte telefon", category="error")
                    return redirect(url_for('views.formular'))
                elif not isTrailer:
                    flash("Žádné vozidlo vybráno", category="error")
                    return redirect(url_for('views.formular'))
                elif not gdpr and not contract and not isCustomer:
                    flash(
                        "Zákazník musí souhlasit s obchodními podmínkami a GDPR.", category="error")
                    return redirect(url_for('views.formular'))

                elif not dateStart:
                    dateStart = datetime.now()
                    dateStart = datetime.strptime(
                        dateStart, "%d. %m. %Y %H:%M")

            if isCustomer and not lastname and not bydliste and not phone:
                customerId = isCustomer.id
                data = pujceno(customer_id=customerId,
                               trailer_id=trailerId, date_created=dateStart, when_back=when_back, TotalPrice=TotalPrice)
                db.session.add(data)
                db.session.commit()

                trail = trailer.query.get(trailerId)
                trail.status = True
                db.session.commit()
                flash('Úspěšně půjčeno', category="success")
                return redirect(url_for('views.formular'))

            else:
                customerId = isCustomer.id
                trailerId = isTrailer.id
                if not isCustomer:
                    data = customer(id_card=id_card, firstname=firstname, lastname=lastname,
                                    bydliste=bydliste, phone=phone, gdpr=gdpr, contract=contract)
                    db.session.add(data)
                    db.session.commit()

                    data = pujceno(customer_id=customerId,
                                   trailer_id=trailerId, date_created=dateStart, when_back=when_back, TotalPrice=TotalPrice)
                    db.session.add(data)
                    db.session.commit()

                    trail = trailer.query.get(trailerId)
                    trail.status = True
                    db.session.commit()

                    flash('Úspěšně půjčeno', category="success")
                    return redirect(url_for('views.formular'))

                else:
                    if phone != isCustomer.phone and len(phone) > 1:
                        isCustomer.phone = phone
                        db.session.commit()

                    if firstname != isCustomer.firstname and len(firstname) > 1:
                        isCustomer.firstname = firstname
                        db.session.commit()

                    if lastname != isCustomer.lastname and len(lastname) > 1:
                        isCustomer.lastname = lastname
                        db.session.commit()

                    if bydliste != isCustomer.bydliste and len(bydliste) > 1:
                        isCustomer.bydliste = bydliste
                        db.session.commit()

                    data = pujceno(customer_id=customerId,
                                   trailer_id=trailerId, date_created=dateStart, when_back=when_back, TotalPrice=TotalPrice)
                    db.session.add(data)
                    db.session.commit()

                    trail = trailer.query.get(trailerId)
                    trail.status = True
                    db.session.commit()

                    flash('Úspěšně půjčeno', category="success")
                    return redirect(url_for('views.formular'))

        return render_template("formular.html", user=current_user, customers=customers, pujceno=pujcen, trailers=trailers, datetime=datetime.now().strftime('%d. %m. %Y %H:%M'), date=datetime.now())

    else:
        return redirect(url_for('views.home'))


# @ views.route("/category", methods=['POST', 'GET'])
# @ login_required
# def add_category():
#     if current_user.name == "admin":
#         isCategory = category.query.all()
#         if request.method == 'POST':
#             name = request.form.get("name")

#             if not name:
#                 flash('Zadejte název kategorie', category="error")
#                 return redirect(url_for('views.add_category'))
#             else:
#                 data = category(name=name)
#                 db.session.add(data)
#                 db.session.commit()
#                 flash('Kategorie byla vytvořena', category="success")
#                 return redirect(url_for('views.add_category'))
#         return render_template("category.html", user=current_user, isCategory=isCategory)


@ views.route("/trailer", methods=['POST', 'GET'])
@ login_required
def add_trailer():
    if current_user.name == "admin":
        isTrailer = trailer.query.order_by(trailer.type.desc()).all()
        if request.method == 'POST':
            name = request.form.get("name")
            spz = request.form.get("spz")
            stk = request.form.get("stk")
            zelkarta = request.form.get("zelkarta")
            price = int(request.form.get('price'))
            img = request.form.get("img")
            serialNumber = request.form.get("serialNumber")
            type = request.form.get("type")
            note = request.form.get("note")

            # isCategory = category.query.filter_by(name=type)

            # for cat in category:
            #     catName = cat.name
            #     catId = cat.id

            if not spz:
                flash("Vyplňte spz", category="error")
                return redirect(url_for('views.add_trailer'))
            elif not stk:
                flash("Vyplňte stk", category="error")
                return redirect(url_for('views.add_trailer'))
            elif not zelkarta:
                flash("Vyplňte zelkarta", category="error")
                return redirect(url_for('views.add_trailer'))

            else:
                stk_string = datetime.strptime(stk, '%d. %m. %Y %H:%M')
                zelkarta_string = datetime.strptime(
                    zelkarta, '%d. %m. %Y %H:%M')
                data = trailer(spz=spz, stk=stk_string,
                               zelkarta=zelkarta_string, price=price, serialNumber=serialNumber, type=type, note=note, name=name)
                db.session.add(data)
                db.session.commit()
                flash('Uloženo', category="success")
                return redirect(url_for('views.add_trailer'))

    else:
        return redirect(url_for('views.home'))

    return render_template("trailer.html", user=current_user, trail=isTrailer, date=datetime.now())


@views.route("/profile/trailer/<trailer_id>", methods=['POST', 'GET'])
@login_required
def profile_trailer(trailer_id):

    isTrailer = trailer.query.filter_by(id=trailer_id).first()

    spz = isTrailer.spz
    stk = isTrailer.stk.strftime('%d. %m. %Y')
    zelkarta = isTrailer.zelkarta.strftime('%d. %m. %Y')
    price = isTrailer.price
    status = isTrailer.status
    type = isTrailer.type

    history = pujceno.query.order_by(
        pujceno.date_created.desc()).filter_by(trailer_id=trailer_id)

    return render_template("trailer_profile.html", user=current_user, spz=spz, stk=stk, zelkarta=zelkarta, price=price, status=status, pujceno=history, type=type)


@views.route("/profile/customer/<customer_id>", methods=['POST', 'GET'])
@login_required
def profile_customer(customer_id):

    isCustomer = customer.query.filter_by(id=customer_id).first()

    firstname = isCustomer.firstname
    lastname = isCustomer.lastname
    phone = isCustomer.phone
    bydliste = isCustomer.bydliste
    id_card = isCustomer.id_card

    history = pujceno.query.order_by(
        pujceno.date_created.desc()).filter_by(customer_id=customer_id)

    return render_template("customer_profile.html", user=current_user, firstname=firstname, lastname=lastname, phone=phone, bydliste=bydliste, id_card=id_card, history=history)


@views.route("/get_back/trailer=<trailer_id>&&pujceno=<pujceno_id>", methods=['POST', 'GET'])
@login_required
def get_back(trailer_id, pujceno_id):
    if request.method == 'POST':
        note = request.form.get("note")
        date_back = request.form.get("date_back")
        date_back = datetime.strptime(date_back, "%d. %m. %Y %H:%M")

        pujcen = pujceno.query.get(pujceno_id)
        pujcen.date_back = date_back
        pujcen.note = note
        db.session.commit()

        data = back(note=note, pujceno_id=pujceno_id, trailer_id=trailer_id)
        db.session.add(data)
        db.session.commit()

        trail = trailer.query.get(trailer_id)
        trail.status = False
        db.session.commit()

        flash('Úspěšně vráceno', category="success")
        return redirect(url_for('views.formular'))


@views.route("/trail/edit%table=<table>%trailer_id=<trailer_id>%pujceno=<pujceno_id>", methods=['POST', 'GET'])
@login_required
def edit(table, trailer_id, pujceno_id):
    if request.method == 'POST':
        if table == "trailer":
            name = request.form.get("name")
            spz = request.form.get("spz")
            stk = request.form.get("stk")
            zelkarta = request.form.get("zelkarta")
            price = int(request.form.get("price"))
            serialNumber = request.form.get("serialNumber")
            note = request.form.get("note")

            stk_string = datetime.strptime(stk, "%d. %m. %Y %H:%M")
            zelkarta_string = datetime.strptime(zelkarta, "%d. %m. %Y %H:%M")

            trail = trailer.query.get(trailer_id)
            trail.spz = spz
            trail.stk = stk_string
            trail.zelkarta = zelkarta_string
            trail.price = price
            trail.serialNumber = serialNumber
            trail.note = note
            trail.name = name
            db.session.commit()
            flash('Změny proběhly v pořádku', category="success")
            return redirect(url_for('views.add_trailer'))

        if table == "pujceno":
            vehicle = request.form.get("trailer")

            isTrailer = trailer.query.filter_by(spz=vehicle).first()
            isPujceno = pujceno.query.filter_by(id=pujceno_id).first()

            trailerId = isTrailer.id
            trailerPrice = isTrailer.price

            dateStart = isPujceno.date_created
            when_back = isPujceno.when_back

            totalDays = math.ceil(
                ((when_back - dateStart).total_seconds())/86400)

            if totalDays < 1:
                TotalPrice = (totalDays + 1) * trailerPrice
            else:
                TotalPrice = totalDays * trailerPrice

            pujcen = pujceno.query.get(pujceno_id)
            pujcen.TotalPrice = TotalPrice
            pujcen.trailer_id = trailerId
            db.session.commit()

            trail = trailer.query.get(trailer_id)
            trail.status = False
            db.session.commit()

            trail = trailer.query.get(trailerId)
            trail.status = True
            db.session.commit()
            flash('Změny proběhly v pořádku', category="success")
            return redirect(url_for('views.formular'))


@views.route("/pdf_generate/pujceno=<pujceno_id>/mail=<mail_status>", methods=['POST', 'GET'])
@login_required
def pdf_contract(pujceno_id, mail_status):

    isPujceno = pujceno.query.filter_by(id=pujceno_id).first()

    firstname = isPujceno.customer.firstname
    lastname = isPujceno.customer.lastname
    id_card = isPujceno.customer.id_card
    bydliste = isPujceno.customer.bydliste
    phone = isPujceno.customer.phone
    spz = isPujceno.trailer.spz
    type = isPujceno.trailer.type
    serialNumber = isPujceno.trailer.serialNumber
    date_created = isPujceno.date_created
    when_back = isPujceno.when_back
    date_back = isPujceno.date_back
    price = isPujceno.trailer.price
    total_time = when_back - date_created
    TotalPrice = isPujceno.TotalPrice
    customerId = isPujceno.customer_id

    total_days = int(total_time.total_seconds()/60/60/24)

    if total_days < 1:
        total_days = 1

    html = render_template("pdf_contract.html", user=current_user, firstname=firstname,
                           lastname=lastname, spz=spz, phone=phone, price=price, id_card=id_card, bydliste=bydliste, date_created=date_created,
                           when_back=when_back, date_back=date_back, total_time=total_time, total_days=total_days, type=type, serialNumber=serialNumber, TotalPrice=TotalPrice)

    pdf = pdfkit.from_string(html)
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=output.pdf"

    # Odesílání emailem

    if mail_status == "False":
        return response

    if mail_status == "True":
        isCustomer = customer.query.filter_by(id=customerId).first()
        email = isCustomer.email
        email_input = request.form.get("email")

        if not email:
            email = request.form.get("email")
            custom = customer.query.get(customerId)
            custom.email = email
            db.session.commit()
            email = custom.email

        if email_input != isCustomer.email:
            email = request.form.get("email")
            custom = customer.query.get(customerId)
            custom.email = email
            db.session.commit()
            email = custom.email

        msg = Message('smlouva.pdf', sender='nakouli@seznam.cz',
                      recipients=[email, "nakouli@seznam.cz"])
        msg.attach("result.pdf", "application/pdf", pdf)
        mail.send(msg)
        flash('Email byl úspěšně odeslán', category="success")
        return redirect(url_for('views.formular'))
    return redirect(url_for('views.formular'))


@views.route("/delete=table=<table>&item=<item_id>", methods=['POST', 'GET'])
@login_required
def delete(table, item_id):

    if table == "trailer":
        data = trailer.query.get(item_id)
        db.session.delete(data)
        db.session.commit()
        flash("úspěšně vymazáno", category="success")
        return redirect(url_for('views.add_trailer'))

    if table == "customer":
        data = customer.query.get(item_id)
        db.session.delete(data)
        db.session.commit()
        flash("úspěšně vymazáno", category="success")
        return redirect(url_for('views.add_trailer'))

    # if table == "category":
    #     data = category.query.get(item_id)
    #     db.session.delete(data)
    #     db.session.commit()
    #     flash("úspěšně vymazáno", category="success")
    #     return redirect(url_for('views.add_category'))
