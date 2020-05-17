from web_app import db

image_keyword_association_table = db.Table(
        'image_keyword_association',
        db.Model.metadata,
        db.Column('image_id', db.Integer, db.ForeignKey('image.id')),
        db.Column('keyword_id', db.Integer, db.ForeignKey('keyword.id')))
