from rest_framework import serializers
from .models import Assessment, WeeklyHealthScore


class AssessmentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Assessment
        fields = ['id', 'user', 'assessment_type', 'score', 'max_score', 'severity', 'answers', 'created_at',
                  'user_name', 'user_email']
        read_only_fields = ['id', 'created_at']


class AssessmentCreateSerializer(serializers.Serializer):
    assessment_type = serializers.ChoiceField(choices=['phq9', 'gad7', 'psqi'])
    score = serializers.IntegerField()
    answers = serializers.ListField(child=serializers.IntegerField())

    def create(self, validated_data):
        assessment_type = validated_data['assessment_type']
        score = validated_data['score']
        answers = validated_data['answers']

        max_scores = {'phq9': 27, 'gad7': 21, 'psqi': 21}
        max_score = max_scores[assessment_type]

        if assessment_type == 'phq9':
            if score <= 4:
                severity = 'Minimal'
            elif score <= 9:
                severity = 'Mild'
            elif score <= 14:
                severity = 'Moderate'
            elif score <= 19:
                severity = 'Moderately Severe'
            else:
                severity = 'Severe'
        elif assessment_type == 'gad7':
            if score <= 4:
                severity = 'Minimal'
            elif score <= 9:
                severity = 'Mild'
            elif score <= 14:
                severity = 'Moderate'
            else:
                severity = 'Severe'
        else:  # psqi
            if score <= 5:
                severity = 'Good'
            elif score <= 10:
                severity = 'Fair'
            elif score <= 15:
                severity = 'Poor'
            else:
                severity = 'Very Poor'

        return Assessment.objects.create(
            user=self.context['request'].user,
            assessment_type=assessment_type,
            score=score,
            max_score=max_score,
            severity=severity,
            answers=answers
        )


class WeeklyHealthScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyHealthScore
        fields = ['id', 'score', 'change', 'week_start', 'created_at']
        read_only_fields = ['id', 'created_at']
