from flask import render_template, flash, redirect, url_for, request

from flask_login import current_user, login_required

from app import db
from app.models import PartDetails, Reclamation, Customer
from app.reclamation import bp
from app.reclamation.forms import ReclamationForm, EditReclamationForm


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
                                      reclamation_part_sn=partDetails_in_database if partDetails_in_database else newPartDetails,
                                      description_reclamation=form.description.data,
                                      status='1')

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
    form = EditReclamationForm(formdata=request.form,
                               obj=rec,
                               customer=rec.reclamation_customer,
                               informed_date=rec.informed_date,
                               due_date=rec.due_date,
                               part_model=rec.reclamation_part_sn.part_no,
                               part_prod_date=rec.reclamation_part_sn.production_date,
                               description=rec.description_reclamation)

    return render_template('reclamation/reclamation.html', form=form, requester=requester)
