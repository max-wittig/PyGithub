from GithubObject import *

from Event import Event
from Hook import Hook
from Authorization import Authorization
from UserKey import UserKey
from AuthenticatedUser import AuthenticatedUser
from NamedUser import NamedUser
from Organization import Organization
from GitRef import GitRef
from GitTree import GitTree
from GitCommit import GitCommit
from GitBlob import GitBlob
from GitTag import GitTag
from Label import Label
from Milestone import Milestone
from IssueComment import IssueComment
from IssueEvent import IssueEvent
from Issue import Issue
from Download import Download
from CommitComment import CommitComment
from Commit import Commit
from Tag import Tag
from Branch import Branch
from PullRequestFile import PullRequestFile
from PullRequestComment import PullRequestComment
from PullRequest import PullRequest
from RepositoryKey import RepositoryKey
from Repository import Repository
from Team import Team

NamedUser._addAttributePolicy(
    ExternalListOfObjects( "orgs", "org", Organization,
        ListGetable( [], [] )
    )
)

__repoElementCreatable = ElementCreatable( [ "name" ], [ "description", "homepage", "private", "has_issues", "has_wiki", "has_downloads", "team_id", ] )
__repoElementGetable = ElementGetable( [ "name" ], [], { "owner" : lambda user: { "login": user.login } } )
__repoListGetable = ListGetable( [], [ "type" ] )
AuthenticatedUser._addAttributePolicy(
    ExternalListOfObjects( "repos", "repo", Repository,
        __repoListGetable,
        __repoElementGetable,
        __repoElementCreatable
    )
)
NamedUser._addAttributePolicy(
    ExternalListOfObjects( "repos", "repo", Repository,
        __repoListGetable,
        __repoElementGetable
    )
)
Organization._addAttributePolicy(
    ExternalListOfObjects( "repos", "repo", Repository,
        __repoListGetable,
        __repoElementGetable,
        __repoElementCreatable
    )
)

AuthenticatedUser._addAttributePolicy(
    ExternalListOfObjects( "watched", "watched", Repository,
        ListGetable( [], [] ),
        ElementAddable(),
        ElementRemovable(),
        ElementHasable()
    )
)
NamedUser._addAttributePolicy(
    ExternalListOfObjects( "watched", "watched", Repository,
        ListGetable( [], [] )
    )
)

def __createForkForUser( user, repo ):
    assert isinstance( repo, Repository )
    return Repository( user._github, user._github._dataRequest( "POST", repo._baseUrl() + "/forks", None, None ), lazy = True )
AuthenticatedUser._addAttributePolicy( SeveralAttributePolicies( [ MethodFromCallable( "create_fork", [ "repo" ], [], __createForkForUser, ObjectTypePolicy( Repository ) ) ], "Forking" ) )
def __createForkForOrg( org, repo ):
    assert isinstance( repo, Repository )
    return Repository( org._github, org._github._dataRequest( "POST", repo._baseUrl() + "/forks", { "org": org.login }, None ), lazy = True )
Organization._addAttributePolicy( SeveralAttributePolicies( [ MethodFromCallable( "create_fork", [ "repo" ], [], __createForkForOrg, ObjectTypePolicy( Repository ) ) ], "Forking" ) )

Organization._addAttributePolicy(
    ExternalListOfObjects( "teams", "team", Team,
        ListGetable( [], [] ),
        ElementCreatable( [ "name" ], [ "repo_names", "permission" ] )
    )
)
Repository._addAttributePolicy(
    ExternalListOfObjects( "teams", "team", Team,
        ListGetable( [], [] )
    )
)

GistComment = GithubObject(
    "GistComment",
    BaseUrl( lambda obj: "/gists/comments/" + str( obj.id ) ),
    InternalSimpleAttributes(
        "id", "url", "body", "created_at",
        "updated_at",
    ),
    InternalObjectAttribute( "user", NamedUser ),
    Editable( [ "body" ], [] ),
    Deletable(),
)

def __isStarred( gist ):
    return gist._github._statusRequest( "GET", gist._baseUrl() + "/star", None, None ) == 204
def __setStarred( gist ):
    gist._github._statusRequest( "PUT", gist._baseUrl() + "/star", None, None )
def __resetStarred( gist ):
    gist._github._statusRequest( "DELETE", gist._baseUrl() + "/star", None, None )
Gist = GithubObject(
    "Gist",
    BaseUrl( lambda obj: "/gists/" + str( obj.id ) ),
    InternalSimpleAttributes(
        "url", "id", "description", "public", "files", "comments", "html_url",
        "git_pull_url", "git_push_url", "created_at", "forks", "history",
        "updated_at",
    ),
    InternalObjectAttribute( "user", NamedUser ),
    Editable( [], [ "description", "files" ] ),
    Deletable(),
    ExternalListOfObjects( "comments", "comment", GistComment,
        ListGetable( [], [] ),
        ElementGetable( [ "id" ], [] ),
        ElementCreatable( [ "body" ], [] ),
    ),
    SeveralAttributePolicies( [
        MethodFromCallable( "is_starred", [], [], __isStarred, SimpleTypePolicy( "bool" ) ),
        MethodFromCallable( "set_starred", [], [], __setStarred, SimpleTypePolicy( None ) ),
        MethodFromCallable( "reset_starred", [], [], __resetStarred, SimpleTypePolicy( None ) ),
    ], "Starring" ),
)
def __createFork( gist ):
    return Gist( gist._github, gist._github._dataRequest( "POST", gist._baseUrl() + "/fork", None, None ), lazy = True )
Gist._addAttributePolicy(    SeveralAttributePolicies( [
        MethodFromCallable( "create_fork", [], [], __createFork, ObjectTypePolicy( Gist ) ),
    ], "Forking" ),
)

NamedUser._addAttributePolicy(
    ExternalListOfObjects( "gists", "gist", Gist,
        ListGetable( [], [] ),
    )
)

AuthenticatedUser._addAttributePolicy(
    ExternalListOfObjects( "gists", "gist", Gist,
        ListGetable( [], [] ),
        ElementCreatable( [ "public", "files", ], [ "description" ] ),
        url = "/gists",
    )
)
def __getStaredGists( user ):
    return [
        Gist( user._github, attributes, lazy = True )
        for attributes in user._github._dataRequest( "GET", "/gists/starred", None, None )
    ]
AuthenticatedUser._addAttributePolicy(
    MethodFromCallable( "get_starred_gists", [], [], __getStaredGists, SimpleTypePolicy( "list of `Gist`" ) ),
)

Event._addAttributePolicy(
    InternalObjectAttribute( "repo", Repository ),
)
Event._addAttributePolicy(
    InternalObjectAttribute( "actor", NamedUser ),
)
Event._addAttributePolicy(
    InternalObjectAttribute( "org", Organization ),
)
