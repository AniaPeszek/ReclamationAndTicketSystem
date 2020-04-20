from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_babelex import _
from flask_login import current_user, login_required
from datetime import datetime

from app import db
from app.models import PartDetails, Reclamation, PartNo
from app.models_serialized import reclamation_schema
from app.reclamation import bp
from app.reclamation.forms import ReclamationForm, EditReclamationForm, ReadOnlyReclamationForm, CloseReclamationForm, \
    ReopenReclamationForm
from app.users.notification import send_message


@bp.route('/reclamation', methods=['GET', 'POST'])
@login_required
def new_reclamation():
    form = ReclamationForm()

    if form.validate_on_submit():
        # checks if parts exists in database
        partDetails_in_database = PartDetails.query.filter_by(part_sn=form.part_sn.data).first()
        if partDetails_in_database is None:
            newPartDetails = PartDetails(part_no=form.part_model.data,
                                         production_date=form.part_prod_date.data,
                                         part_sn=form.part_sn.data)

        # create new claim

        new_reclamation = Reclamation(reclamation_requester=current_user,
                                      reclamation_customer=form.customer.data,
                                      informed_date=form.informed_date.data,
                                      due_date=form.due_date.data,
                                      reclamation_part_sn_id=partDetails_in_database if partDetails_in_database else newPartDetails,
                                      description_reclamation=form.description.data)

        db.session.add(new_reclamation)
        db.session.commit()

        part = new_reclamation.reclamation_part_sn_id
        if part.part_no.part_no_person_in_charge:
            recepient = part.part_no.part_no_person_in_charge
            send_message(Reclamation, new_reclamation.id, recepient)

        flash('Reclamation has been added')

        reclamation = Reclamation.query.filter_by(id=new_reclamation.id).first_or_404()

        return redirect(url_for('reclamation_bp.reclamation', reclamation_number=reclamation.id))

    return render_template('reclamation/new_reclamation.html', form=form)


@bp.route('/reclamation/<reclamation_number>', methods=['GET', 'POST'])
@login_required
def reclamation(reclamation_number):
    rec = Reclamation.query.get(reclamation_number)
    requester = rec.reclamation_requester.username
    tickets = rec.tickets.all()
    close_form = CloseReclamationForm()
    open_form = ReopenReclamationForm()

    part_details = db.session.query(PartDetails).filter_by(id=rec.reclamation_part_sn_id.id).first()
    person_in_charge = part_details.part_no.person_in_charge
    users_who_can_edit = [rec.reclamation_requester, rec.reclamation_requester.team.team_leader, person_in_charge]

    if current_user in users_who_can_edit:

        if rec.status == 0:
            status = _("Open")
            form = EditReclamationForm(formdata=request.form,
                                       obj=rec,
                                       customer=rec.reclamation_customer,
                                       informed_date=rec.informed_date,
                                       due_date=rec.due_date,
                                       part_model=rec.reclamation_part_sn_id.part_no,
                                       part_sn=rec.reclamation_part_sn_id.part_sn,
                                       part_prod_date=rec.reclamation_part_sn_id.production_date,
                                       description=rec.description_reclamation,
                                       finished_date=rec.finished_date, )
            if close_form.submit1.data and close_form.validate():
                rec.finished_date = datetime.utcnow()
                rec.status = 1
                db.session.add(rec)
                db.session.commit()
                flash('Reclamation has been closed')
                return redirect(url_for('reclamation_bp.reclamation', reclamation_number=rec.id))
        else:
            status = _("Closed")
            form = ReadOnlyReclamationForm(formdata=request.form,
                                           obj=rec,
                                           customer=rec.reclamation_customer,
                                           informed_date=rec.informed_date,
                                           due_date=rec.due_date,
                                           part_model=rec.reclamation_part_sn_id.part_no,
                                           part_sn=rec.reclamation_part_sn_id.part_sn,
                                           part_prod_date=rec.reclamation_part_sn_id.production_date,
                                           description=rec.description_reclamation,
                                           finished_date=rec.finished_date)
            if open_form.submit1.data and open_form.validate():
                rec.finished_date = None
                rec.status = 0
                db.session.add(rec)
                db.session.commit()
                flash('Reclamation has been re-opened')
                return redirect(url_for('reclamation_bp.reclamation', reclamation_number=rec.id))


    else:
        form = ReadOnlyReclamationForm(formdata=request.form,
                                       obj=rec,
                                       customer=rec.reclamation_customer,
                                       informed_date=rec.informed_date,
                                       due_date=rec.due_date,
                                       part_model=rec.reclamation_part_sn_id.part_no,
                                       part_sn=rec.reclamation_part_sn_id.part_sn,
                                       part_prod_date=rec.reclamation_part_sn_id.production_date,
                                       description=rec.description_reclamation,
                                       finished_date=rec.finished_date)
        if rec.status == 0:
            status = _("Open")
        else:
            status = _("Closed")

    if form.submit.data and form.validate():

        # checks if parts exists in database
        partDetails_in_database = PartDetails.query.filter_by(part_sn=form.part_sn.data).first()
        if partDetails_in_database is None:
            newPartDetails = PartDetails(part_no=form.part_model.data,
                                         production_date=form.part_prod_date.data,
                                         part_sn=form.part_sn.data)

        # edit the claim

        rec.reclamation_customer = form.customer.data
        rec.informed_date = form.informed_date.data
        rec.due_date = form.due_date.data
        rec.reclamation_part_sn_id = partDetails_in_database if partDetails_in_database else newPartDetails
        rec.description_reclamation = form.description.data
        rec.finished_date = form.finished_date.data
        if rec.finished_date is None:
            rec.status = 0
        else:
            rec.status = 1
        db.session.add(rec)
        db.session.commit()
        flash('Reclamation has been edited')
        return redirect(url_for('reclamation_bp.reclamation', reclamation_number=rec.id))

    if current_user in users_who_can_edit:
        return render_template('reclamation/reclamation.html', form=form, requester=requester, status=status, rec=rec,
                           tickets=tickets, close_form=close_form, open_form=open_form, can_edit=True)
    else:
        return render_template('reclamation/reclamation.html', form=form, requester=requester, status=status, rec=rec,
                               tickets=tickets, can_edit=False)


@bp.route('/all')
@bp.route('/all/<int:page_num>')
@login_required
def all_reclamations(page_num=1):
    reclamations = Reclamation.query.order_by(Reclamation.finished_date). \
        paginate(page=page_num, per_page=current_app.config['ELEMENTS_PER_PAGE'], error_out=False)
    return render_template('reclamation/all.html', reclamations=reclamations)


@bp.route('/reclamation_get_data', methods=['GET', 'POST'])
@login_required
def reclamations_data():
    reclamations = Reclamation.query.all()
    output = reclamation_schema.dump(reclamations)
    return jsonify({"reclamations": output})


@bp.route('/reclamations/all', methods=['GET', 'POST'])
@login_required
def reclamations_all():
    return render_template('reclamation/reclamations_all.html')
