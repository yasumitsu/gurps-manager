"""Database schema for GURPS Manager.

It is possible to generate a diagram of the schema defined herein. See the
readme for details.

If a model does not specify a primary key, django automatically generates a
column named ``id``. Django will not generate ``id`` if you pass ``primary_key =
True`` to some other column.

"""
import re
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models

# pylint: disable=R0903
# "Too few public methods (0/2)"
# It is both common and OK for a model to have no methods.
#
# pylint: disable=W0232
# "Class has no __init__ method"
# It is both common and OK for a model to have no __init__ method.

def validate_quarter(number):
    """Check whether ``number`` is some multiple of 0.25.

    If check fails, raise a ``ValidationError``.

    ``number`` is a float.

    >>> from django.core.exceptions import ValidationError
    >>> validate_quarter(0.0)
    >>> validate_quarter(0.25)
    >>> validate_quarter(0.50)
    >>> try:
    ...     validate_quarter(0.26)
    ... except ValidationError:
    ...     'an exception was raised'
    'an exception was raised'

    """
    if Decimal(number).quantize(Decimal('0.01')) % Decimal(0.25) \
    != Decimal(0.00):
        raise ValidationError('{} is not divisible by 0.25.'.format(number))

class Campaign(models.Model):
    """A single role-playing campaign."""
    MAX_LEN_NAME = 50
    MAX_LEN_DESCRIPTION = 2000

    # many-to-many fields
    skillsets = models.ManyToManyField(SkillSet)

    # string-based fields
    name = models.CharField(max_length = MAX_LEN_NAME)
    description = models.TextField(
        max_length = MAX_LEN_DESCRIPTION,
        blank = True
    )

class SkillSet(models.Model):
    """A grouping of similar skills"""
    MAX_LEN_NAME = 50

    # string-based fields
    name = models.CharField(max_length = MAX_LEN_NAME)

class Character(models.Model):
    """An individual who can be role-played."""
    MAX_LEN_NAME = 50
    MAX_LEN_DESCRIPTION = 2000
    MAX_LEN_STORY = 2000

    # key fields
    campaign = models.ForeignKey(Campaign)

    # many-to-many fields
    skills = models.ManyToManyField(Skill, through='CharacterSkill')
    spells = models.ManyToManyField(Spell, through='CharacterSpell')
    items = models.ManyToManyField(Item, through='Possession')

    # string-based fields
    name = models.CharField(max_length = MAX_LEN_NAME)
    description = models.TextField(
        max_length = MAX_LEN_DESCRIPTION,
        blank = True,
    )
    story = models.TextField(
        max_length = MAX_LEN_STORY,
        blank = True,
    )

    # integer fields
    strength = models.IntegerField()
    dexterity = models.IntegerField()
    intelligence = models.IntegerField()
    health = models.IntegerField()
    magery = models.IntegerField()
    bonus_fatigue = models.IntegerField()
    bonus_hitpoints = models.IntegerField()
    bonus_alertness = models.IntegerField()
    bonus_willpower = models.IntegerField()
    bonus_fright = models.IntegerField()
    bonus_speed = models.IntegerField()
    bonus_movement = models.IntegerField()
    bonus_dodge = models.IntegerField()
    bonus_initiative = models.IntegerField()
    free_strength = models.IntegerField()
    free_dexterity = models.IntegerField()
    free_intelligence = models.IntegerField()
    free_health = models.IntegerField()

    # float fields
    total_points = models.FloatField(validators=[validate_quarter])
    used_fatigue = models.FloatField(validators=[validate_quarter])

    # lookup fields
    appearance = models.IntegerField()
    wealth = models.IntegerField()
    eidetic_memory = models.IntegerField()
    muscle_memory = models.IntegerField()

    # derived fields
    def fatigue(self):
        """Returns a character's total fatigue"""
        return self.strength + self.bonus_fatigue

    def hitpoints(self):
        """Returns a character's total hitpoints"""
        return self.health + self.bonus_hitpoints

    def alertness(self):
        """Returns a character's alertness"""
        return self.intelligence + self.bonus_alertness

    def will(self):
        """Returns a character's will"""
        return self.intelligence + self.bonus_will

    def fright(self):
        """Returns a character's fright"""
        return self.intelligence + self.bonus_fright

class Trait(models.Model):
    """An Advantage or Disadvantage that a character may have"""
    MAX_LEN_NAME = 50
    MAX_LEN_DESCRIPTION = 2000

    # key fields
    character = models.ForeignKey(Character)

    # string-based fields
    name = models.CharField(max_length = MAX_LEN_NAME)
    description = models.TextField(
        max_length = MAX_LEN_DESCRIPTION,
        blank = True,
    )

    # float fields
    points = models.FloatField(validators=[validate_quarter])

class Skill(models.Model):
    """A skill available to characters.

    A skill is some task that a character has some proficency in. For example, a
    character could become proficent in dagger throwing or underwater basket
    weaving.

    """
    MAX_LEN_NAME = 50

    CATEGORY_CHOICES = (
        (1, 'Mental'),
        (2, 'Mental (health)'),
        (3, 'Physical'),
        (4, 'Physical (health)'),
    )
    DIFFICULTY_CHOICES = (
        (1, 'Easy'),
        (2, 'Average'),
        (3, 'Hard'),
        (4, 'Very Hard'),
    )

    # key fields
    skillset = models.ForeignKey(SkillSet)

    # string-based fields
    name = models.CharField(max_length = MAX_LEN_NAME)

    # lookup fields
    category = models.IntegerField(choices=CATEGORY_CHOICES)
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES)

class CharacterSkill(models.Model):
    """A skill that a character possesses"""
    
    # key fields
    skill = models.ForeignKey(Skill)
    character = models.ForeignKey(Character)

    # integer fields
    bonus_level = models.IntegerField()

    # float fields
    points = models.FloatField(validators=[validate_quarter])

class Spell(models.Model):
    """A Spell available to characters

    Anything from fireballs to feather falling

    """
    MAX_LEN_NAME = 50
    MAX_LEN_SCHOOL = 50
    MAX_LEN_RESIST = 50

    DIFFICULTY_CHOICES = (
        (1, 'Hard'),
        (2, 'Very Hard'),
    )

    # string-based fields
    name = models.CharField(max_length = MAX_LEN_NAME)
    school = models.CharField(max_length = MAX_LEN_SCHOOL)
    resist = models.CharField(max_length = MAX_LEN_RESIST)

    # integer fields
    cast_time = models.IntegerField()
    duration = models.IntegerField()
    initial_fatigue_cost = models.IntegerField()
    maintainance_fatigue_cost = models.IntegerField() 

    # lookup fields
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES)

class CharacterSpell(models.Model):
    """A spell that a character may know"""
    
    # key fields
    spell = models.ForeignKey(Spell)
    character = models.ForeignKey(Character)

    # integer fields
    bonus_level = models.IntegerField()

    # float fields
    points = models.FloatField(validators=[validate_quarter])

class Item(models.Model):
    """An item that a character may possess"""
    MAX_LEN_NAME = 50
    MAX_LEN_DESCRIPTION = 2000

    # string-based fields
    name = models.CharField(max_length = MAX_LEN_NAME)
    description = models.TextField(
        max_length = MAX_LEN_DESCRIPTION,
        blank = True,
    )

    # float fields
    cost = models.FloatField()
    weight = models.FloatField()

class Possession(models.Model):
    """An item that a character possesses"""
    
    # key fields
    item = models.ForeignKey(Item)
    character = models.ForeignKey(Character)

    # integer fields
    quantity = models.IntegerField()

class HitLocation(models.Model):
    """A location on a character that can be affected

    Affectations include: armor value, damage, status effects, etc. 

    """
    MAX_LEN_NAME = 50
    MAX_LEN_STATUS = 500

    # key fields
    character = models.ForeignKey(Character)

    # string-based fields
    name = models.CharField(max_length = MAX_LEN_NAME)
    status = models.TextField(
        max_length = MAX_LEN_STATUS,
        blank = True,
    )

    # integer fields
    passive_damage_resistance = models.IntegerField()
    damage_resistance = models.IntegerField()
    damage_taken = models.IntegerField()