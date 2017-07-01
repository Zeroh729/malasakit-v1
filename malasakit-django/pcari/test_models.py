from __future__ import unicode_literals
import math

from django.test import TestCase

from pcari.models import Respondent
from pcari.models import QuantitativeQuestion, QualitativeQuestion
from pcari.models import QuantitativeQuestionRating, Comment, CommentRating


class StatisticsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.question = QuantitativeQuestion.objects.create()
        QuantitativeQuestionRating.objects.bulk_create([
            QuantitativeQuestionRating(
                question=cls.question,
                score=score,
                respondent=Respondent.objects.create()
            ) for score in [-1, 9, 3, 3, 4, -1]
        ])

        cls.question_no_ratings = QuantitativeQuestion.objects.create()

        cls.comment = Comment.objects.create(
            question=QualitativeQuestion.objects.create(),
            language='en',
            message='Hello world',
            respondent=Respondent.objects.create(),
        )
        CommentRating.objects.bulk_create([
            CommentRating(
                comment=cls.comment,
                score=score,
                respondent=Respondent.objects.create()
            ) for score in [-2, 0, 3]
        ])

    def test_num_ratings(self):
        self.assertEqual(self.question.num_ratings, 4)
        QuantitativeQuestionRating.objects.create(
            question=self.question,
            score=6,
            respondent=Respondent.objects.create()
        )
        self.assertEqual(self.question.num_ratings, 5)
        self.assertEqual(self.question_no_ratings.num_ratings, 0)
        self.assertEqual(self.comment.num_ratings, 2)

    def test_mean_score(self):
        self.assertAlmostEqual(self.question.mean_score, 19.0/4)
        self.assertTrue(math.isnan(self.question_no_ratings.mean_score))
        self.assertAlmostEqual(self.comment.mean_score, 1.5)
        CommentRating.objects.get(score=3).delete()
        self.assertAlmostEqual(self.comment.mean_score, 0)

    def test_mode_score(self):
        self.assertEqual(self.question.mode_score, 3)
        QuantitativeQuestionRating.objects.filter(score=3).update(score=9)
        self.assertEqual(self.question.mode_score, 9)
        self.assertNotEqual(self.comment.mode_score,
                            QuantitativeQuestionRating.NOT_RATED)

    def test_score_stdev(self):
        self.assertAlmostEqual(self.question.score_stdev, 2.87228132327)
        self.assertAlmostEqual(self.comment.score_stdev, 4.5**0.5)
        CommentRating.objects.get(score=3).delete()
        self.assertTrue(math.isnan(self.comment.score_stdev))

    def test_score_sem(self):
        self.assertAlmostEqual(self.question.score_sem, 1.436140662)
        QuantitativeQuestionRating.objects.all().delete()
        self.assertTrue(math.isnan(self.question.score_sem))
        self.assertAlmostEqual(self.comment.score_sem, 2.25**0.5)
