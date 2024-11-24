# Domain Driven Design (DDD)

We need to create an abstraction of the domain. We learn a lot about a domain while talking with the domain experts. But this raw knowledge is
not going to be easily transformed into software constructs, unless we build an abstraction of it, a blueprint in our minds.

What is this abstraction? It is a model, a model
of the domain. According to Eric Evans, a domain model is not a
particular diagram; it is the idea that the diagram is intended to
convey. It is not just the knowledge in a domain expert’s head; it
is a rigorously organized and selective abstraction of that
knowledge. A diagram can represent and communicate a model,
as can carefully written code, as can an English sentence.

A domain contains just too much
information to include it all into the model. And much of it is not
even necessary to be considered. This is a challenge by itself.
What to keep and what to throw away? It’s part of the design,
the software creation process.

We are not alone in
this process, so we need to share knowledge and information,
and we need to do it well, precisely, completely, and without
ambiguity. we need to communicate
the model.

When we have a model expressed, we can start doing code
design. This is different from software design. Software design
is like creating the architecture of a house, it’s about the big
picture. On the other hand, code design is working on the details,
like the location of a painting on a certain wall.

Nonetheless the final product won’t be good
without good code design. Here code design patterns come
handy, and they should be applied when necessary.

## There are different approaches to software design.

### One is the waterfall design method:

The business experts put up a set of requirements which
are communicated to the business analysts. The analysts create a
model based on those requirements, and pass the results to the
developers, who start coding based on what they have received.
It’s a one way flow of knowledge.

### Another approach is the Agile methodologies, such as Extreme Programming (XP). 

These methodologies are a collective
movement against the waterfall approach, resulting from the
difficulties of trying to come up with all the requirements
upfront.

The Agile methods have their own problems and limitations;
they advocate simplicity, but everybody has their own view of
what that means. Also, continuous refactoring done by
developers without solid design principles will produce code that
is hard to understand or change. And while the waterfall
approach may lead to over-engineering, the fear of overengineering may lead to another fear: the fear of doing a deep,
thoroughly thought out design.

# I. Building Domain Knowledge

In order to be able to build up a model you need to
extract essential information and generalize it.

Domain experts know their area of expertise well, but they organize and use their
knowledge in a specific way, which is not always the best to be
implemented into a software system. The analytical mind of the
software designer helps unearth some of the key concepts of the domain during discussions.

# II. The Ubiquitous Language

it is absolutely necessary
to develop a model of the domain by having the the software
specialists work with the domain experts; however, that
approach usually has some initial difficulties due to a
fundamental communication barrier.

The terminology of day-to-day discussions is disconnected from
the terminology embedded in the code (ultimately the most
important product of a software project).

We tend to use our own dialects during these design sessions,
but none of these dialects can be a common language because
none serves everyone’s needs.

> <b> A core principle of domain-driven design is to use a language
based on the model. </b>

Use the model as the backbone of a language. Request that the
team use the language consistently in all communications, and
also in the code.

Domain experts should object to terms or structures that are
awkward or inadequate to convey domain understanding. If
domain experts cannot understand something in the model or the
language, then it is most likely that there is something is wrong
with it. On the other hand, developers should watch for
ambiguity or inconsistency that will tend to appear in design.

## Creating the Ubiquitous Language

UML cannot convey
two important aspects of a model: the meaning of the concepts it
represents and what the objects are supposed to do. But that is
OK, since we can add other communication tools to do it. 

We can use documents. One advisable way of communicating
the model is to make some small diagrams each containing a
subset of the model. These diagrams would contain several
classes, and the relationship between them. That already
includes a good portion of the concepts involved. Then we can
add text to the diagram. The text will explain behavior and
constraints which the diagram cannot.

Those documents can be even hand-drawn, because that
transmits the feeling that they are temporary, and might be
changed in the near future, which is true, because the model is
changed many times in the beginning before it reaches a more
stable status.

> <b> It might be tempting to try to create one large diagram over the
entire model. But it will be so cluttered
that it will not convey the understanding better then did the
collection of small diagrams. </b>

*Creating multiple small models/diagrams, then organize them into a larger unified model when your understanding has been sufficient built-up*

## how do we approach the transition from model to code? 

> <b> One of the recommended design techniques is the so called
analysis model. </b>

which is seen as separate from code design and
is usually done by different people. The analysis model is the
result of business domain analysis, resulting in a model which
has no consideration for the software used for implementation.
Such a model is used to understand the domain.

> <b> Object-oriented programming is another good technique. </b>

Object-oriented programming is suitable for model
implementation because they are both based on the same
paradigm. Object-oriented programming provides classes of
objects and associations of classes, object instances, and
messaging between them. OOP languages make it possible to
create direct mappings between model objects with their
relationships, and their programming counterparts. 

> <b> Procedural programming languages (C, Cobol) is not recommended for model-driven design. </b>

A program written in a procedural language is usually perceived as a set of
functions, one calling another, and working together to achieve a
certain result. Such a program cannot easily encapsulate
conceptual connections, making mapping between domain and
code difficult to be realized. 

# III. The Building Blocks Of A Model-Driven Design

![DDD bulding blocks](Images/DDD.png)

## Layered Architecture 

when domain-related code is mixed with the other
layers, it becomes extremely difficult to see and think about.
Superficial changes to the UI can actually change business logic.
To change a business rule may require meticulous tracing of UI
code, database code, or other program elements. Implementing
coherent, model-driven objects becomes impractical. Automated
testing is awkward.

> <b> Therefore, partition a complex program into LAYERS. Develop
a design within each LAYER that is cohesive and that depends
only on the layers below. Follow standard architectural patterns
to provide loose coupling to the layers above. </b>

*Concentrate all the code related to the domain model in one layer and isolate it from the user interface, application, and infrastructure code.*

<b> A common architectural solution for domain-driven designs contain four conceptual layers:</b>

+ <b>User Interface</b> (Presentation Layer): Responsible for presenting information to the user and interpreting user commands.
+ <b>Application</b> Layer: This is a thin layer which coordinates the application activity. It does not contain business logic. It does not hold the state of the business objects, but it can hold the state of an application task progress.
+ <b>Domain</b> Layer: This layer contains information about the domain. This is the heart of the business software. The state of business objects is held here.
+ <b>Infrastructure</b> Layer: This layer acts as a supporting library for all the other layers. It provides communication between layers, implements persistence for business objects, contains supporting libraries for the user interface layer, etc.

It is important to divide an application in separate layers, and
establish rules of interactions between the layers. If the code is
not clearly separated into layers, it will soon become so
entangled that it becomes very difficult to manage changes.

For example, a typical interaction of the application, domain and
infrastructure could look like this. The user wants to book a
flights route, and asks an application service in the application
layer to do so. The application tier fetches the relevant domain
objects from the infrastructure and invokes relevant methods on
them, e.g., to check security margins to other already booked
flights. Once the domain objects have made all checks and
updated their status to “decided”, the application service persists
the objects to the infrastructure.