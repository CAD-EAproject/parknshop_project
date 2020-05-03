from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from app import current_app, db
from app.product.forms import CategoriesForm, SubCategoriesForm, ProductBrandForm, ProductForm, RatingForm
from app.models import SubCategories, Categories, ProductBrand, Product, Promotion, Review
from app.product import bp
from sqlalchemy import func


@bp.route('/show_product/<int:id>', methods=['GET', 'POST'])
def show_product(id):
    form = ProductForm()
    form.catid.choices = [(c.id, c.subcategories) for c in db.session.query(SubCategories).all()]
    form.pdbid.choices = [(p.id, p.productbrand) for p in db.session.query(ProductBrand).all()]
    if form.validate_on_submit():
        add_product = Product(product=form.product.data, volumn=form.volumn.data,
                              price=form.price.data, details=form.details.data,
                              origin=form.origin.data, productimage=form.url.data,
                              categories_id=form.catid.data, productbrand_id=form.pdbid.data,
                              pricedown=form.pricedown.data)
        db.session.add(add_product)
        db.session.commit()
        flash(_('New Product added'))
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    showproduct = SubCategories.query.get_or_404(id)
    breadcrumb = SubCategories.query.filter_by(id=showproduct.id)
    products = Product.query.filter_by(categories_id=showproduct.id).paginate(
        page, current_app.config['PRODUCT_PER_PAGE'], False)
    categoriess = Categories.query.order_by(Categories.categories)
    subcats = SubCategories.query.order_by(SubCategories.subcategories)
    promotions = Promotion.query.order_by(Promotion.id)
    next_url = url_for('product.show_product', id=showproduct.id, page=products.next_num) \
        if products.has_next else None
    prev_url = url_for('product.show_product', id=showproduct.id, page=products.prev_num) \
        if products.has_prev else None
    return render_template('product/show_product.html', title=_('Categories'), form=form,
                           products=products.items, categoriess=categoriess, subcats=subcats,
                           breadcrumb=breadcrumb, promotions=promotions,
                           page=page, next_url=next_url, prev_url=prev_url)

@bp.route('/create_product', methods=['GET', 'POST'])
@login_required
def create_product():
    form = ProductForm()
    form.catid.choices = [(c.id, c.subcategories) for c in db.session.query(SubCategories).all()]
    form.pdbid.choices = [(p.id, p.productbrand) for p in db.session.query(ProductBrand).all()]
    if form.validate_on_submit():
        product = Product(product=form.product.data, volumn=form.volumn.data,
                          price=form.price.data, pricedown=form.pricedown.data ,details=form.details.data,
                          origin=form.origin.data, productimage=form.url.data,
                          categories_id=form.catid.data, productbrand_id=form.pdbid.data)
        db.session.add(product)
        db.session.commit()
        flash(_('New Product added'))
        return redirect(url_for('product.create_product'))
    products = Product.query.order_by(Product.id)
    return render_template('product/create_product.html', title=_('Create Product'),
                           form=form, products=products)

@bp.route('/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(request.form)
    form.catid.choices = [(s.id, s.subcategories) for s in db.session.query(SubCategories).all()]
    form.pdbid.choices = [(p.id, p.productbrand) for p in db.session.query(ProductBrand).all()]
    if form.validate_on_submit():
        product.product = form.product.data
        product.volumn = form.volumn.data
        product.price = form.price.data
        product.pricedown = form.pricedown.data
        product.details = form.details.data
        product.origin = form.origin.data
        product.productimage = form.url.data
        product.categories_id = form.catid.data
        product.productbrand_id = form.pdbid.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.index'))
    elif request.method == 'GET':
        form.product.data = product.product
        form.volumn.data = product.volumn
        form.price.data = product.price
        form.pricedown.data = product.pricedown
        form.details.data = product.details
        form.origin.data = product.origin
        form.url.data = product.productimage
        form.catid.data = product.categories_id
        form.pdbid.data = product.productbrand_id
    return render_template('product/edit_product.html', title=_('Edit Product Brand'),
                           form=form, product=product)

@bp.route('/delete_product/<int:id>')
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    product.promotions = []
    db.session.commit()
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('main.index'))

@bp.route('/add_promotion/<int:id1>/<int:id2>', methods=['GET', 'POST'])
@login_required
def add_promotion(id1, id2):
    addproduct = Product.query.get_or_404(id1)
    addpromotion = Promotion.query.get_or_404(id2)
    try:
        addpromotion.products.append(addproduct)
        db.session.commit()
        flash(_('Product added to Promotion'))
    except:
        flash(_('Multiple input'))
    return redirect(url_for('main.index'))

@bp.route('/remove_promotion/<int:id1>/<int:id2>', methods=['GET', 'POST'])
@login_required
def remove_promotion(id1, id2):
    addproduct = Product.query.get_or_404(id2)
    addpromotion = Promotion.query.get_or_404(id1)
    addpromotion.products.remove(addproduct)
    db.session.commit()
    flash(_('Product removed from Promotion'))
    return redirect(url_for('main.index'))







