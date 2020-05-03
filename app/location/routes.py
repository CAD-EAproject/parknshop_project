from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from app import current_app, db
from app.location.forms import StoreForm, RegionForm, DistrictForm, CompanyBrandForm
from app.models import User, Store, Region, District, CompanyBrand
from app.location import bp

@bp.route('/store')
def store():
    stores = Store.query.order_by(Store.store)
    districts = District.query.order_by(District.district)
    regions = Region.query.order_by(Region.region)
    return render_template("location/store.html", title=_('Store Location'),
                           stores=stores, districts=districts, regions=regions,)

@bp.route('/create_store', methods=['GET', 'POST'])
@login_required
def create_store():
    form = StoreForm()
    form.district.choices = [(d.id, d.district) for d in db.session.query(District).all()]
    form.cobrand.choices = [(c.id, c.companybrand) for c in db.session.query(CompanyBrand).all()]
    if form.validate_on_submit():
        store = Store(store=form.store.data, address=form.address.data,
                      district_id=form.district.data, tel=form.tel.data,
                      companybrand_id=form.cobrand.data)
        db.session.add(store)
        db.session.commit()
        flash(_('New store added'))
        return redirect(url_for('location.create_store'))
    page = request.args.get('page', 1, type=int)
    stores = Store.query.order_by(Store.store.desc()).paginate(
        page, current_app.config['STORES_PER_PAGE'], False)
    next_url = url_for('location.create_store', page=stores.next_num) \
        if stores.has_next else None
    prev_url = url_for('location.create_store', page=stores.prev_num) \
        if stores.has_prev else None
    return render_template('location/create_store.html', title=_('Create Store'),
                           stores=stores.items, form=form, page=page,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/edit_store/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_store(id):
    store = Store.query.get_or_404(id)
    form = StoreForm(request.form)
    form.district.choices = [(d.id, d.district) for d in db.session.query(District).all()]
    form.cobrand.choices = [(c.id, c.companybrand) for c in db.session.query(CompanyBrand).all()]
    if form.validate_on_submit():
        store.store = form.store.data
        store.address = form.address.data
        store.district_id = form.district.data
        store.companybrand_id = form.cobrand.data
        store.tel = form.tel.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('location.create_store'))
    elif request.method == 'GET':
        form.store.data = store.store
        form.address.data = store.address
        form.district.data = store.district_id
        form.cobrand.data = store.companybrand_id
        form.tel.data = store.tel
    return render_template('location/edit_store.html', title=_('Edit Store'),
                           form=form, store=store)

@bp.route('/delete_store/<int:id>')
@login_required
def delete_store(id):
    store = Store.query.get_or_404(id)
    db.session.delete(store)
    db.session.commit()
    return redirect(url_for('location.create_store'))

@bp.route('/create_district', methods=['GET', 'POST'])
@login_required
def create_district():
    form1 = DistrictForm()
    form2 = RegionForm()
    form1.region.choices = [(r.id, r.region) for r in db.session.query(Region).all()]
    if form1.validate_on_submit():
        district = District(district=form1.district.data, region_id=form1.region.data)
        db.session.add(district)
        db.session.commit()
        flash(_('New district added'))
        return redirect(url_for('location.create_district'))
    elif form2.validate_on_submit():
        region = Region(region=form2.region.data)
        db.session.add(region)
        db.session.commit()
        flash(_('New region added'))
        return redirect(url_for('location.create_district'))
    districts = District.query.order_by(District.district.desc())
    regions = Region.query.order_by(Region.region)
    return render_template('location/create_district.html', title=_('Create District'),
                           form1=form1, form2=form2,
                           regions=regions, districts=districts)

@bp.route('/edit_district/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_district(id):
    district = District.query.get_or_404(id)
    form = DistrictForm(request.form)
    form.region.choices = [(r.id, r.region) for r in db.session.query(Region).all()]
    if form.validate_on_submit():
        district.district = form.district.data
        district.region_id = form.region.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('location.create_district'))
    elif request.method == 'GET':
        form.district.data = district.district
    return render_template('location/edit_district.html', title=_('Edit District'),
                           form=form, district=district)

@bp.route('/delete_district/<int:id>')
@login_required
def delete_district(id):
    districtid = District.query.get_or_404(id)
    db.session.delete(districtid)
    db.session.commit()
    return redirect(url_for('location.create_district'))

@bp.route('/delete_region/<int:id>')
@login_required
def delete_region(id):
    regionid = Region.query.get_or_404(id)
    db.session.delete(regionid)
    db.session.commit()
    return redirect(url_for('location.create_district'))

@bp.route('/companybrand', methods=['GET', 'POST'])
@login_required
def companybrand():
    form = CompanyBrandForm()
    if form.validate_on_submit():
        companybrand = CompanyBrand(companybrand=form.brand.data, photourl=form.image.data)
        db.session.add(companybrand)
        db.session.commit()
    cobrands = CompanyBrand.query.order_by(CompanyBrand.id)
    return render_template('location/companybrand.html', title=_('Edit Company Brand'), cobrands=cobrands, form=form)

@bp.route('/edit_CoBrand/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_CoBrand(id):
    companybrand = CompanyBrand.query.get_or_404(id)
    form = CompanyBrandForm(request.form)
    if form.validate_on_submit():
        companybrand.companybrand = form.brand.data
        companybrand.photourl = form.image.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('location.companybrand'))
    elif request.method == 'GET':
        form.brand.data = companybrand.companybrand
        form.image.data = companybrand.photourl
    return render_template('location/edit_CoBrand.html', title=_('Edit CoBrand'),
                           form=form, companybrand=companybrand)

@bp.route('/delete_CoBrand/<int:id>')
@login_required
def delete_CoBrand(id):
    companybrand = CompanyBrand.query.get_or_404(id)
    db.session.delete(companybrand)
    db.session.commit()
    return redirect(url_for('location.companybrand'))

