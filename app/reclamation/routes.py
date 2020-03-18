from flask import render_template, flash, redirect, url_for

from flask_login import current_user, login_required

from app import db
from app.models import PartDetails, Reclamation
from app.reclamation import bp
from app.reclamation.forms import ReclamationForm


@login_required
@bp.route('/reclamation', methods=['GET', 'POST'])
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
                                      finished_date=form.finished_date.data,
                                      reclamation_part_sn=partDetails_in_database if partDetails_in_database else newPartDetails,
                                      description_reclamation=form.description.data,
                                      status='1')

        db.session.add(new_reclamation)
        db.session.commit()
        flash('Reclamation has been added')

        reclamation = Reclamation.query.filter_by(id=new_reclamation.id).first_or_404()

        #Do poprawy odniesienie
        # return redirect(url_for('reclamation_bp.reclamation', reclamation=reclamation))
        return render_template('reclamation/new_reclamation.html', form=form)

    return render_template('reclamation/new_reclamation.html', form=form)


@login_required
@bp.route('/reclamation/<reclamation_number>')
def reclamation(reclamation_number):
    reclamation = Reclamation.query.filter_by(id=reclamation_number).first_or_404()

    return render_template('reclamation/reclamation.html', reclamation=reclamation)
