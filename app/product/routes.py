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

@bp.route('/reviews/<int:id1>/<int:id2>', methods=['GET', 'POST'])
def reviews(id1, id2):
    pro_categories = SubCategories.query.get_or_404(id1)
    re_product = Product.query.get_or_404(id2)
    if Review.query.filter(Review.product_id == re_product.id).count() > 0:
        rating1 = (db.session.query(func.avg(Review.rating1)).filter(Review.product_id == re_product.id).scalar()) * 20
        rating2 = (db.session.query(func.avg(Review.rating2)).filter(Review.product_id == re_product.id).scalar()) * 20
        rating3 = (db.session.query(func.avg(Review.rating3)).filter(Review.product_id == re_product.id).scalar()) * 20
        rating4 = (db.session.query(func.avg(Review.rating4)).filter(Review.product_id == re_product.id).scalar()) * 20
    else:
        rating1 = 0
        rating2 = 0
        rating3 = 0
        rating4 = 0
    total = Review.query.filter(Review.product_id == re_product.id).count()
    subcategories = pro_categories.id
    review_comment = Review.query.filter(Review.product_id == re_product.id)
    return render_template('product/reviews.html', title=_('Reviews'), rating1=rating1,
                           rating2=rating2, rating3=rating3, rating4=rating4, total=total,
                           subcategories=subcategories, review_comment=review_comment,
                           pro_categories=pro_categories, re_product=re_product)

@bp.route('/create_reviews/<int:id1>/<int:id2>', methods=['GET', 'POST'])
def create_reviews(id1, id2):
    form = RatingForm()
    pro_categories = SubCategories.query.get_or_404(id1)
    re_product = Product.query.get_or_404(id2)
    if form.validate_on_submit():
        product_review = Review(rating1=form.rating1.data, rating2=form.rating2.data,
                                rating3=form.rating3.data, rating4=form.rating4.data,
                                comment=form.comment.data, product_id=re_product.id)
        db.session.add(product_review)
        db.session.commit()
        flash(_('Reviews added, Thank you!'))
        return redirect('/reviews/{id_1}/{id_2}'.format(id_1=id1, id_2=id2))
    subcategories = pro_categories.id
    return render_template('product/create_reviews.html', title=_('Create Reviews'),
                           form=form, pro_categories=pro_categories, re_product=re_product)

@bp.route('/remove_reviews/<int:id1>/<int:id2>/<int:id3>')
@login_required
def remove_reviews(id1, id2, id3):
    de_review = Review.query.get_or_404(id3)
    db.session.delete(de_review)
    db.session.commit()
    flash(_('Review removed'))
    return redirect('/reviews/{id_1}/{id_2}'.format(id_1=id1, id_2=id2))


@bp.route('/edit_reviews/<int:id1>/<int:id2>/<int:id3>', methods=['GET', 'POST'])
@login_required
def edit_reviews(id1, id2, id3):
    ed_review = Review.query.get_or_404(id3)
    pro_categories = SubCategories.query.get_or_404(id1)
    re_product = Product.query.get_or_404(id2)
    form = RatingForm(request.form)
    if form.validate_on_submit():
        ed_review.rating1 = form.rating1.data
        ed_review.rating2 = form.rating2.data
        ed_review.rating3 = form.rating3.data
        ed_review.rating4 = form.rating4.data
        ed_review.comment = form.comment.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect('/reviews/{id_1}/{id_2}'.format(id_1=id1, id_2=id2))
    elif request.method == 'GET':
        form.rating1.data = ed_review.rating1
        form.rating2.data = ed_review.rating2
        form.rating3.data = ed_review.rating3
        form.rating4.data = ed_review.rating4
        form.comment.data = ed_review.comment
    return render_template('product/edit_reviews.html', title=_('Edit Reviews'),
                           form=form, re_product=re_product, pro_categories=pro_categories, ed_review=ed_review)

@bp.route('/create_categories', methods=['GET', 'POST'])
@login_required
def create_categories():
    form = CategoriesForm()
    subform = SubCategoriesForm()
    subform.catid.choices = [(c.id, c.categories) for c in db.session.query(Categories).all()]
    if form.validate_on_submit():
        categories = Categories(categories=form.cat.data)
        db.session.add(categories)
        db.session.commit()
        flash(_('New categories added'))
        return redirect(url_for('product.create_categories'))
    elif subform.validate_on_submit():
        subcategories = SubCategories(subcategories=subform.subcat.data, categories_id=subform.catid.data)
        db.session.add(subcategories)
        db.session.commit()
        flash(_('New Sub-Categories added'))
        return redirect(url_for('product.create_categories'))
    categoriess = Categories.query.order_by(Categories.id)
    subcategoriess = SubCategories.query.order_by(SubCategories.categories_id)
    return render_template('product/create_categories.html', title=_('Create Categories'),
                           form=form, subcategoriess=subcategoriess, categoriess=categoriess, subform=subform)

@bp.route('/edit_categories/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_categories(id):
    categoriesid = Categories.query.get_or_404(id)
    form = CategoriesForm(request.form)
    if form.validate_on_submit():
        categoriesid.categories = form.cat.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('product.create_categories'))
    elif request.method == 'GET':
        form.cat.data = categoriesid.categories
    return render_template('product/edit_categories.html', title=_('Edit Categories'),
                           form=form, categoriesid=categoriesid)

@bp.route('/edit_subcategories/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_subcategories(id):
    subcategoriesid = SubCategories.query.get_or_404(id)
    form = SubCategoriesForm(request.form)
    form.catid.choices = [(c.id, c.categories) for c in db.session.query(Categories).all()]
    if form.validate_on_submit():
        subcategoriesid.subcategories = form.subcat.data
        subcategoriesid.categories_id = form.catid.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('product.create_categories'))
    elif request.method == 'GET':
        form.subcat.data = subcategoriesid.subcategories
        form.catid.data = subcategoriesid.categories_id
    return render_template('product/edit_subcategories.html', title=_('Edit Sub-Categories'),
                           form=form, subcategoriesid=subcategoriesid)

@bp.route('/delete_categories/<int:id>')
@login_required
def delete_categories(id):
    delete_categories = Categories.query.get_or_404(id)
    db.session.delete(delete_categories)
    db.session.commit()
    return redirect(url_for('product.create_categories'))

@bp.route('/delete_subcategories/<int:id>')
@login_required
def delete_subcategories(id):
    delete_subcategories = SubCategories.query.get_or_404(id)
    db.session.delete(delete_subcategories)
    db.session.commit()
    return redirect(url_for('product.create_categories'))

@bp.route('/delete_productbrand/<int:id>')
@login_required
def delete_productbrand(id):
    delete_brand = Categories.query.get_or_404(id)
    db.session.delete(delete_brand)
    db.session.commit()
    return redirect(url_for('product.create_categories'))

@bp.route('/productbrand', methods=['GET', 'POST'])
@login_required
def productbrand():
    form = ProductBrandForm()
    if form.validate_on_submit():
        productbrand = ProductBrand(productbrand=form.PoBrand.data, imgurl=form.url.data)
        db.session.add(productbrand)
        db.session.commit()
        flash(_('New Product Brand added'))
        return redirect(url_for('product.productbrand'))
    productbrands = ProductBrand.query.order_by(ProductBrand.id)
    return render_template('product/productbrand.html', title=_('Create Product Brand'),
                           form=form, productbrands=productbrands)

@bp.route('/edit_PoBrand/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_PoBrand(id):
    productbrand = ProductBrand.query.get_or_404(id)
    form = ProductBrandForm(request.form)
    if form.validate_on_submit():
        productbrand.productbrand = form.PoBrand.data
        productbrand.imgurl = form.url.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('product.productbrand'))
    elif request.method == 'GET':
        form.PoBrand.data = productbrand.productbrand
        form.url.data = productbrand.imgurl
    return render_template('product/edit_PoBrand.html', title=_('Edit Product Brand'),
                           form=form, productbrand=productbrand)

@bp.route('/delete_PoBrand/<int:id>')
@login_required
def delete_PoBrand(id):
    productbrand = ProductBrand.query.get_or_404(id)
    db.session.delete(productbrand)
    db.session.commit()
    return redirect(url_for('product.productbrand'))





