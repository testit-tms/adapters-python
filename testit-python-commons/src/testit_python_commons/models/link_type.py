import enum


class LinkType(enum.Enum):
    RELATED = 'Related'
    BLOCKED_BY = 'BlockedBy'
    DEFECT = 'Defect'
    ISSUE = 'Issue'
    REQUIREMENT = 'Requirement'
    REPOSITORY = 'Repository'
