from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int()
    email = fields.Email(required=True)
    password = fields.Str(required=True)

