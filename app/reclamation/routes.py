from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_babelex import _
from flask_login import current_user, login_required

from app import db
from app.models import PartDetails, Reclamation
from app.models_serialized import reclamation_schema
from app.reclamation import bp
from app.reclamation.forms import ReclamationForm, EditReclamationForm, ReadOnlyReclamationForm, CreateTickedForm


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
        flash('Reclamation has been added')

        reclamation = Reclamation.query.filter_by(id=new_reclamation.id).first_or_404()

        return redirect(url_for('reclamation_bp.reclamation', reclamation_number=str(reclamation.id)))

    return render_template('reclamation/new_reclamation.html', form=form)


@bp.route('/reclamation/<reclamation_number>', methods=['GET', 'POST'])
@login_required
def reclamation(reclamation_number):
    rec = Reclamation.query.get(reclamation_number)
    requester = rec.reclamation_requester.username
    status = _("Open") if rec.status == 0 else _("Closed")
    if current_user.id == rec.reclamation_requester.id:
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
                                       finished_date=rec.finished_date, )

    form_create_ticket = CreateTickedForm()
    if form_create_ticket.validate_on_submit():
        return redirect(url_for('ticket_bp.new_ticket', rec_id=rec.id))

    if form.validate_on_submit():

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
        try:
            if rec.finished_date < rec.informed_date:
                flash('Finished date can not be earlier than Informed Date')
                return redirect(url_for('reclamation_bp.reclamation', reclamation_number=str(rec.id)))
        finally:
            db.session.add(rec)
            db.session.commit()
            flash('Reclamation has been edited')
            return redirect(url_for('reclamation_bp.reclamation', reclamation_number=str(rec.id)))

    return render_template('reclamation/reclamation.html', form=form, requester=requester, status=status, rec=rec,
                           form_ticket=form_create_ticket)


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
