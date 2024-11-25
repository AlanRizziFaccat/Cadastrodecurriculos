from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError

class Cadastro_curriculoForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    telefone = StringField('Telefone', validators=[])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    endereco_web = StringField('Endereço Web')
    experiencia_profissional = TextAreaField('Experiência Profissional', validators=[DataRequired()])
    submit = SubmitField('Cadastrar')

    # Validação personalizada para telefone
    def validate_telefone(self, field):
        if field.data and not field.data.isnumeric():
            raise ValidationError("O telefone deve conter apenas números.")
