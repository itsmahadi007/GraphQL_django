import graphene

from graphene_django import DjangoObjectType, DjangoListField
from .models import Book


# BookType adapts the Book model to a DjangoObjectType. We set fields to __all__ to indicate
# that we want all the fields in the model available in our API.
class BookType(DjangoObjectType):
    class Meta:
        model = Book
        fields = "__all__"


# This Query class defines the GraphQL queries that the API will provide to clients. The "all_books" query will return a
# list of all the BookType instances, while the book query will return one BookType instance, given by an integer ID.
# The class defines two methods, which are the query “resolvers”. Every query in the schema maps to a resolver method.
class Query(graphene.ObjectType):
    all_books = graphene.List(BookType)
    book = graphene.Field(BookType, book_id=graphene.Int())
    review = graphene.Field(BookType, book_review=graphene.Int())

    # The two query resolvers query the database using the Django model to execute the query and return the results.
    def resolve_all_books(self, info, **kwargs):  # get all the data from this table
        return Book.objects.all()

    def resolve_book(self, info, book_id):  # get only specific data from this table
        return Book.objects.get(pk=book_id)

    def resolve_review(self, info, book_review):  # filter data that match with review number from this table
        return Book.objects.filter(review__exact=book_review)


# The BookInput class defines fields similar to our Book model object to allow the client to add or change the data
# through the API. We will use this class as an argument for our mutation classes.
class BookInput(graphene.InputObjectType):
    id = graphene.ID()
    title = graphene.String()
    author = graphene.String()
    year_published = graphene.String()
    review = graphene.Int()


# The CreateBook class will be used to create and save new Book entries to the database. For every mutation class we
# must have an Arguments inner class and a mutate() class method.
class CreateBook(graphene.Mutation):
    class Arguments:
        book_data = BookInput(required=True)

    # We defined an instance of the BookInput class we created earlier as our arguments, and we made it mandatory
    # with the required=True option. After that we defined the model we are working with by doing this book =
    # graphene.Field(BookType).
    book = graphene.Field(BookType)

    # In the mutate method we are saving a new book by calling the save() method on a new Book instance created from
    # the book_data values passed as argument.
    @staticmethod
    def mutate(root, info, book_data=None):
        book_instance = Book(
            title=book_data.title,
            author=book_data.author,
            year_published=book_data.year_published,
            review=book_data.review
        )
        book_instance.save()
        return CreateBook(book=book_instance)


# The UpdateBook mutation class is very similar to CreateBook. The difference here is the logic in the mutate()
# method, which retrieves a particular book object from the database by the book ID provided and then applies the
# changes from the input argument to it.
class UpdateBook(graphene.Mutation):
    class Arguments:
        book_data = BookInput(required=True)

    book = graphene.Field(BookType)

    @staticmethod
    def mutate(root, info, book_data=None):
        book_instance = Book.objects.get(pk=book_data.id)

        if book_instance:
            book_instance.title = book_data.title
            book_instance.author = book_data.author
            book_instance.year_published = book_data.year_published
            book_instance.review = book_data.review
            book_instance.save()

            return UpdateBook(book=book_instance)
        return UpdateBook(book=None)


# In the DeleteBook mutation class we have graphene.ID as the only argument. The mutate() method uses this id to
# remove the referenced book from the database.
class DeleteBook(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    book = graphene.Field(BookType)

    @staticmethod
    def mutate(root, info, id):
        book_instance = Book.objects.get(pk=id)
        book_instance.delete()

        return None


# We now have two queries and three mutations defined. To register these with Graphene, we wrote below code
class Mutation(graphene.ObjectType):
    create_book = CreateBook.Field()
    update_book = UpdateBook.Field()
    delete_book = DeleteBook.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
