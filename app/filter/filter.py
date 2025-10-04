from app.projects.models import Project
from sqlalchemy import or_


def get_filter_data():
    # Get Project Attributes for Filters
    try:
        sectors_from_db = Project.query.with_entities(
            Project.sector).distinct().all()
        people_counts_from_db = Project.query.with_entities(
            Project.people_count).distinct().all()
        skills_from_db = Project.query.with_entities(
            Project.skills).distinct().all()

        # Transform from tuples to lists
        sectors = [row.sector for row in sectors_from_db]
        people_counts = [row.people_count for row in people_counts_from_db]
        skills = set()
        for row in skills_from_db:
            if row.skills:
                skills.update(
                    [skill.strip() for skill in row.skills.split(',')])
        skills = list(skills)

        sectors.sort()
        people_counts.sort()
        skills.sort()

    except Exception as e:
        # Handle error gracefully, e.g., log it
        sectors, people_counts, skills = [], [], []
        print(f"Error occurred while fetching project filter data: {e}")

    return {
        'sectors': sectors,
        'people_counts': people_counts,
        'skills': skills
    }


def filter_projects(options):
    """Filter projects based on provided options"""
    try:
        query = Project.query

        # Handle sectors
        if 'sectors' in options and options['sectors']:
            sectors = options['sectors']

            # Ensure sectors is always a list
            if isinstance(sectors, str):
                sectors = [sectors]

            # Filter if not 'all' selected
            if sectors and 'all' not in sectors:
                query = query.filter(Project.sector.in_(sectors))

        if 'people_count' in options and options['people_count']:
            people_count = options['people_count']
            if isinstance(people_count, str):
                people_count = [people_count]

            if people_count and 'all' not in people_count:
                count_filters = []
                for count in people_count:
                    if count == '2-3':
                        count_filters.append(
                            Project.people_count.between(2, 3))
                    elif count == '4-6':
                        count_filters.append(
                            Project.people_count.between(4, 6))
                    elif count == '7+':
                        count_filters.append(Project.people_count >= 7)
                if count_filters:
                    query = query.filter(or_(*count_filters))

        if 'skills' in options and options['skills']:
            skills = options['skills']
            if isinstance(skills, str):
                skills = [skills]
            if skills and 'all' not in skills:
                skill_filters = []
                for skill in skills:
                    skill_filters.append(Project.skills.like(f"%{skill}%"))
                query = query.filter(or_(
                    *skill_filters))

    except Exception as e:
        print(f"Error occurred while filtering projects: {e}")
        return []

    return query.order_by(Project.id.desc()).all()


# Let's add a simple helper function for single sector filtering
def get_projects_by_sector(sector_name):
    """Simple function to get projects by single sector (for learning)"""
    if sector_name and sector_name.lower() != 'all':
        return filter_projects({'sector': sector_name})
    else:
        return Project.query.order_by(Project.id.desc()).all()
