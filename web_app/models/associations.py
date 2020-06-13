from web_app import db

image_keyword_association_table = db.Table(
        'image_keyword_association',
        db.Model.metadata,
        db.Column('image_id', db.Integer, db.ForeignKey('image.id')),
        db.Column('keyword_id', db.Integer, db.ForeignKey('keyword.id')))

album_image_association_table = db.Table(
        'album_image_association',
        db.Model.metadata,
        db.Column('album_id', db.Integer, db.ForeignKey('album.id')),
        db.Column('image_id', db.Integer, db.ForeignKey('image.id')))

portfolio_album_association_table = db.Table(
        'portfolio_album_association',
        db.Model.metadata,
        db.Column('album_id', db.Integer, db.ForeignKey('album.id')),
        db.Column('portfolio_id', db.Integer, db.ForeignKey('portfolio.id')))

thumbnail_image_association_table = db.Table(
        'thumbnail_image_association',
        db.Model.metadata,
        db.Column('thumbnail_id', db.Integer, db.ForeignKey('thumbnail_image.id')),
        db.Column('image_id', db.Integer, db.ForeignKey('image.id')))

downsampled_image_association_table = db.Table(
        'downsampled_image_association',
        db.Model.metadata,
        db.Column('downsampled_id', db.Integer, db.ForeignKey('downsampled_image.id')),
        db.Column('image_id', db.Integer, db.ForeignKey('image.id')))
