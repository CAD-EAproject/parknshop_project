from datetime import datetime
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from app import current_app, db
from app.main.forms import EditProfileForm, PostForm, PromotionForm, FeatureForm, BannerForm
from app.product.forms import ProductForm
from app.models import SubCategories, Categories, ProductBrand, Promotion, Banner, Post, User, Feature, \
                        Product, Review
from app.main import bp
from sqlalchemy import func


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())

@bp.route('/maintenance')
def maintenance():
    flash(_('Sorry! Our system is updating.'))
    return redirect(url_for('main.index'))

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    form1 = BannerForm()
    form2 = PromotionForm()
    form3 = FeatureForm()
    productform = ProductForm()
    productform.catid.choices = [(c.id, c.subcategories) for c in db.session.query(SubCategories).all()]
    productform.pdbid.choices = [(p.id, p.productbrand) for p in db.session.query(ProductBrand).all()]
    if productform.validate_on_submit():
        product = Product(product=productform.product.data, volumn=productform.volumn.data,
                          price=productform.price.data, details=productform.details.data,
                          origin=productform.origin.data, productimage=productform.url.data,
                          categories_id=productform.catid.data, productbrand_id=productform.pdbid.data,
                          pricedown=productform.pricedown.data)
        db.session.add(product)
        db.session.commit()
        flash(_('New Product added'))
        return redirect(url_for('main.index'))
    elif form3.validate_on_submit():
        feature=Feature(title=form3.title.data, description=form3.description.data, url=form3.url.data)
        db.session.add(feature)
        db.session.commit()
        flash(_('New Promotion added'))
        return redirect(url_for('main.index'))
    elif form2.validate_on_submit():
        promotion=Promotion(name=form2.name.data, url=form2.url.data)
        db.session.add(promotion)
        db.session.commit()
        flash(_('New Promotion added'))
        return redirect(url_for('main.index'))
    elif form1.validate_on_submit():
        banneritem=Banner(banner=form1.banner.data)
        db.session.add(banneritem)
        db.session.commit()
        flash(_('New Banner added'))
        return redirect(url_for('main.index'))
    banners = Banner.query.order_by(Banner.id)
    categoriess = Categories.query.order_by(Categories.categories)
    subcats = SubCategories.query.order_by(SubCategories.subcategories)
    promotions = Promotion.query.order_by(Promotion.id)
    features = Feature.query.all()
    page = request.args.get('page', 1, type=int)
    pdbrands = ProductBrand.query.order_by(func.random()).paginate(
        page, current_app.config['PRODUCTBRAND_PER_PAGE'], False)
    newproducts = Product.query.order_by(Product.id.desc()).paginate(
        page, current_app.config['NEWPRODUCT_PER_PAGE'], False)
    reviews = Review.query.all()
    return render_template('index.html', title=_('Home'), form1=form1, form2=form2, form3=form3,
                           banners=banners, categoriess=categoriess, subcats=subcats,
                           newproducts=newproducts.items, promotions=promotions, features=features,
                           pdbrands=pdbrands.items, page=page, productform=productform, reviews=reviews)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('main.user', username=username))
