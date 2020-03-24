from flask import render_template, flash, redirect, url_for, request, jsonify, current_app

from flask_login import current_user, login_required

from app import db, ma
from app.models import PartDetails, Reclamation, Customer, PartNo, User
from app.reclamation import bp
from app.reclamation.forms import ReclamationForm, EditReclamationForm, ReadOnlyReclamationForm

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_marshmallow.fields import Hyperlinks, URLFor


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
    status = rec.status
    if current_user.id == rec.reclamation_requester.id:
        form = EditReclamationForm(formdata=request.form,
                                   obj=rec,
                                   customer=rec.reclamation_customer,
                                   informed_date=rec.informed_date,
                                   due_date=rec.due_date,
                                   part_model=rec.reclamation_part_sn.part_no,
                                   part_prod_date=rec.reclamation_part_sn.production_date,
                                   description=rec.description_reclamation,
                                   finished_date=rec.finished_date, )
    else:
        form = ReadOnlyReclamationForm(formdata=request.form,
                                       obj=rec,
                                       customer=rec.reclamation_customer,
                                       informed_date=rec.informed_date,
                                       due_date=rec.due_date,
                                       part_model=rec.reclamation_part_sn.part_no,
                                       part_prod_date=rec.reclamation_part_sn.production_date,
                                       description=rec.description_reclamation,
                                       finished_date=rec.finished_date, )

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
        rec.reclamation_part_sn = partDetails_in_database if partDetails_in_database else newPartDetails
        rec.description_reclamation = form.description.data
        rec.finished_date = form.finished_date.data
        if rec.finished_date is None:
            rec.status = "Open"
        else:
            rec.status = "Closed"
        try:
            if rec.finished_date < rec.informed_date:
                flash('Finished date can not be earlier than Informed Date')
                return redirect(url_for('reclamation_bp.reclamation', reclamation_number=str(rec.id)))
        finally:
            db.session.add(rec)
            db.session.commit()
            flash('Reclamation has been edited')
            return redirect(url_for('reclamation_bp.reclamation', reclamation_number=str(rec.id)))

    return render_template('reclamation/reclamation.html', form=form, requester=requester, status=status, rec=rec)


@bp.route('/all')
@bp.route('/all/<int:page_num>')
@login_required
def all_reclamations(page_num=1):
    reclamations = Reclamation.query.order_by(Reclamation.finished_date). \
        paginate(page=page_num, per_page=current_app.config['ELEMENTS_PER_PAGE'], error_out=False)
    return render_template('reclamation/all.html', reclamations=reclamations)

# jak już będzie działać ok, to przenieść do app.models
class PartDetailsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PartDetails
        # include_fk = True


class PartNoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PartNo


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User


class ReclamationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Reclamation
        # include_fk = True

    _links = Hyperlinks({'self': URLFor('reclamation_bp.reclamation', reclamation_number=str(id))})


user_schema = UserSchema(many=True)
part_no_schema = PartNoSchema(many=True)
part_detail_schema = PartDetailsSchema(many=True)
reclamation_schema = ReclamationSchema(many=True)


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
