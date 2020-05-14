from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
    jsonify,
    current_app,
    send_from_directory,
    abort,
)
from flask_babelex import _
from flask_login import current_user, login_required
from datetime import datetime

from app import db
from app.models import PartDetails, Reclamation, PartNo, Note, File
from app.models_serialized import reclamation_schema
from app.reclamation import bp
from app.reclamation.forms import (
    ReclamationForm,
    EditReclamationForm,
    ReadOnlyReclamationForm,
    CloseReclamationForm,
    ReopenReclamationForm,
    NoteForm,
)
from app.users.notification import send_message

from werkzeug.utils import secure_filename
import os
import secrets
from string import ascii_letters
import json


@bp.route("/reclamation", methods=["GET", "POST"])
@login_required
def new_reclamation():
    form = ReclamationForm()

    if form.validate_on_submit():
        # checks if parts exists in database
        partDetails_in_database = PartDetails.query.filter_by(
            part_sn=form.part_sn.data
        ).first()
        if partDetails_in_database is None:
            newPartDetails = PartDetails(
                part_no=form.part_model.data,
                production_date=form.part_prod_date.data,
                part_sn=form.part_sn.data,
            )

        # create new claim

        new_reclamation = Reclamation(
            reclamation_requester=current_user,
            reclamation_customer=form.customer.data,
            informed_date=form.informed_date.data,
            due_date=form.due_date.data,
            reclamation_part_sn_id=partDetails_in_database
            if partDetails_in_database
            else newPartDetails,
            description_reclamation=form.description.data,
        )

        db.session.add(new_reclamation)
        db.session.commit()

        part = new_reclamation.reclamation_part_sn_id
        if part.part_no.part_no_person_in_charge:
            recepient = part.part_no.part_no_person_in_charge
            send_message(Reclamation, new_reclamation.id, recepient)

        flash("Reclamation has been added")

        reclamation = Reclamation.query.filter_by(id=new_reclamation.id).first_or_404()

        return redirect(
            url_for("reclamation_bp.reclamation", reclamation_number=reclamation.id)
        )

    return render_template("reclamation/new_reclamation.html", form=form)


@bp.route("/reclamation/<reclamation_number>", methods=["GET", "POST"])
@login_required
def reclamation(reclamation_number):
    rec = Reclamation.query.get(reclamation_number)
    requester = (
        rec.reclamation_requester.first_name + " " + rec.reclamation_requester.last_name
    )
    tickets = rec.tickets.all()
    close_form = CloseReclamationForm()
    open_form = ReopenReclamationForm()
    note_form = NoteForm()
    notes = Note.query.filter_by(rec_id=reclamation_number).all()
    files = db.session.query(File).filter_by(reclamation_id=reclamation_number).all()

    part_details = (
        db.session.query(PartDetails)
        .filter_by(id=rec.reclamation_part_sn_id.id)
        .first()
    )
    person_in_charge = part_details.part_no.person_in_charge
    users_who_can_edit = [
        rec.reclamation_requester,
        rec.reclamation_requester.team.team_leader,
        person_in_charge,
    ]

    if current_user in users_who_can_edit:

        if rec.status == 0:
            status = _("Open")
            form = EditReclamationForm(
                formdata=request.form,
                obj=rec,
                customer=rec.reclamation_customer,
                informed_date=rec.informed_date,
                due_date=rec.due_date,
                part_model=rec.reclamation_part_sn_id.part_no,
                part_sn=rec.reclamation_part_sn_id.part_sn,
                part_prod_date=rec.reclamation_part_sn_id.production_date,
                description=rec.description_reclamation,
                finished_date=rec.finished_date,
            )
            if close_form.submit1.data and close_form.validate():
                rec.finished_date = datetime.utcnow()
                rec.status = 1
                db.session.add(rec)
                db.session.commit()
                flash("Reclamation has been closed")
                return redirect(
                    url_for("reclamation_bp.reclamation", reclamation_number=rec.id)
                )
        else:
            status = _("Closed")
            form = ReadOnlyReclamationForm(
                formdata=request.form,
                obj=rec,
                customer=rec.reclamation_customer,
                informed_date=rec.informed_date,
                due_date=rec.due_date,
                part_model=rec.reclamation_part_sn_id.part_no,
                part_sn=rec.reclamation_part_sn_id.part_sn,
                part_prod_date=rec.reclamation_part_sn_id.production_date,
                description=rec.description_reclamation,
                finished_date=rec.finished_date,
            )
            if open_form.submit1.data and open_form.validate():
                rec.finished_date = None
                rec.status = 0
                db.session.add(rec)
                db.session.commit()
                flash("Reclamation has been re-opened")
                return redirect(
                    url_for("reclamation_bp.reclamation", reclamation_number=rec.id)
                )

    else:
        form = ReadOnlyReclamationForm(
            formdata=request.form,
            obj=rec,
            customer=rec.reclamation_customer,
            informed_date=rec.informed_date,
            due_date=rec.due_date,
            part_model=rec.reclamation_part_sn_id.part_no,
            part_sn=rec.reclamation_part_sn_id.part_sn,
            part_prod_date=rec.reclamation_part_sn_id.production_date,
            description=rec.description_reclamation,
            finished_date=rec.finished_date,
        )
        if rec.status == 0:
            status = _("Open")
        else:
            status = _("Closed")

    if form.submit.data and form.validate():

        # checks if parts exists in database
        partDetails_in_database = PartDetails.query.filter_by(
            part_sn=form.part_sn.data
        ).first()
        if partDetails_in_database is None:
            newPartDetails = PartDetails(
                part_no=form.part_model.data,
                production_date=form.part_prod_date.data,
                part_sn=form.part_sn.data,
            )

        # edit the claim

        rec.reclamation_customer = form.customer.data
        rec.informed_date = form.informed_date.data
        rec.due_date = form.due_date.data
        rec.reclamation_part_sn_id = (
            partDetails_in_database if partDetails_in_database else newPartDetails
        )
        rec.description_reclamation = form.description.data
        rec.finished_date = form.finished_date.data
        if rec.finished_date is None:
            rec.status = 0
        else:
            rec.status = 1
        db.session.add(rec)
        db.session.commit()
        flash("Reclamation has been edited")
        return redirect(
            url_for("reclamation_bp.reclamation", reclamation_number=rec.id)
        )

    if note_form.submit2.data and note_form.validate():
        new_note = Note(
            note_drafter=current_user, rec=rec, content=note_form.content.data
        )
        db.session.add(new_note)
        db.session.commit()
        flash("The note has been added")
        return redirect(
            url_for("reclamation_bp.reclamation", reclamation_number=rec.id)
        )

    if current_user in users_who_can_edit:
        return render_template(
            "reclamation/reclamation.html",
            form=form,
            requester=requester,
            status=status,
            rec=rec,
            tickets=tickets,
            close_form=close_form,
            open_form=open_form,
            can_edit=True,
            notes=notes,
            note_form=note_form,
            files=files,
        )
    else:
        return render_template(
            "reclamation/reclamation.html",
            form=form,
            requester=requester,
            status=status,
            rec=rec,
            tickets=tickets,
            can_edit=False,
            notes=notes,
            note_form=note_form,
            files=files,
        )


@bp.route("/all")
@bp.route("/all/<int:page_num>")
@login_required
def all_reclamations(page_num=1):
    reclamations = Reclamation.query.order_by(Reclamation.finished_date).paginate(
        page=page_num, per_page=current_app.config["ELEMENTS_PER_PAGE"], error_out=False
    )
    return render_template("reclamation/all.html", reclamations=reclamations)


@bp.route("/reclamation_get_data", methods=["GET", "POST"])
@login_required
def reclamations_data():
    reclamations = Reclamation.query.all()
    output = reclamation_schema.dump(reclamations)
    return jsonify({"reclamations": output})


@bp.route("/reclamations/all", methods=["GET", "POST"])
@login_required
def reclamations_all():
    return render_template("reclamation/reclamations_all.html")


def allowed_file(filename):
    if not "." in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in current_app.config["ALLOWED_EXTENSIONS"]


def allowed_filesize(filesize):
    return int(filesize) <= current_app.config["MAX_FILE_FILESIZE"]


@bp.route("/upload_file/<int:rec_id>", methods=["GET", "POST"])
@login_required
def upload_file(rec_id):
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        if request.files:
            if not allowed_filesize(request.cookies.get("filesize")):
                flash("File exceeded maximum size.")
                return redirect(request.url)

            file = request.files["file"]
            if file.filename == "":
                flash("File must have a filename")
                return redirect(request.url)

            if not allowed_file(file.filename):
                flash("That file extension is not allowed")
                return redirect(request.url)
            else:
                filename = secure_filename(file.filename)
                reclamation_id = rec_id
                existing_filenames = get_filenames_for_reclamation(reclamation_id)
                if filename in existing_filenames:
                    flash(
                        "File with this name already exists. You can change name and try again."
                    )
                    return redirect(request.url)
                secure_dirname = "".join(
                    secrets.choice(ascii_letters) for _ in range(10)
                )
                dirname = f"reclamation_{reclamation_id}"

                if not os.path.exists(
                    os.path.join(current_app.config["UPLOAD_FOLDER"], dirname)
                ):
                    os.mkdir(os.path.join(current_app.config["UPLOAD_FOLDER"], dirname))

                dir_path = os.path.join(
                    current_app.config["UPLOAD_FOLDER"], dirname, secure_dirname
                )
                if not os.path.exists(dir_path):
                    os.mkdir(dir_path)

                path = os.path.join(dir_path, filename)
                file.save(path)

                relative_path = os.path.join(dirname, secure_dirname, filename)
                file_data = File(
                    name=filename,
                    relative_path=relative_path,
                    reclamation_id=reclamation_id,
                )
                db.session.add(file_data)
                db.session.commit()

                flash("File saved")
                return redirect(
                    url_for(
                        "reclamation_bp.reclamation", reclamation_number=reclamation_id
                    )
                )

    return render_template("reclamation/upload_file.html", rec_id=rec_id)


@bp.route("/get_file/<path:path>")
@login_required
def get_file(path):
    path_to_uploads = os.path.join(current_app.config["UPLOAD_FOLDER"])
    try:
        return send_from_directory(path_to_uploads, filename=path, as_attachment=True)
    except FileNotFoundError:
        abort(404)


def get_filenames_for_reclamation(reclamation_id):
    files = db.session.query(File.name).filter_by(reclamation_id=reclamation_id).all()
    return [file[0] for file in files]


@bp.route("/delete_file/<path:path>", methods=["DELETE"])
@login_required
def delete_file(path):
    relative_path = path
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], path)
    try:
        if os.path.exists(path):
            os.remove(path)
            print(os.path.dirname(path))
            if not os.listdir(os.path.dirname(path)):
                os.rmdir(os.path.dirname(path))
        file_data = (
            db.session.query(File).filter_by(relative_path=relative_path).first()
        )
        db.session.delete(file_data)
        db.session.commit()
        return json.dumps({"status": "OK"})
    except Exception as e:
        return json.dumps({"status": str(e)})


@bp.route("/edit_note/<note_id>", methods=["POST"])
def edit_note(note_id):
    try:
        note_to_edit = Note.query.get(note_id)
        data = request.get_json()
        note_to_edit.content = data["note_text"]
        db.session.commit()
        return json.dumps({"status": "OK"})
    except Exception as e:
        return json.dumps({"status": str(e)})


@bp.route("/delete_note/<note_id>", methods=["DELETE"])
def delete_note(note_id):
    try:
        note_to_delete = Note.query.get(note_id)
        db.session.delete(note_to_delete)
        db.session.commit()
        return json.dumps({"status": "OK"})
    except Exception as e:
        return json.dumps({"status": str(e)})
