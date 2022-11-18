# Notification lambdas
A collection of Docker lambda functions and images that are used as part of the Notify service.

## Lambdas
- [Blazer](./blazer/README.md): an instance of Blazer that uses Devise and Google OAuth for authentication.
- [Google CIDR](./google-cidr/README.md): a function that updates an AWS managed prefix list with a list of Google service CIDR ranges.

## Adding a new lambda
1. Run `make lambda` and provide a name for your lambda's folder.
1. Add your lambda's folder name to the `matrix` sections of the GitHub workflows.  You can find the ones you need to update with `make matrix`.
1. Update this readme with a link to your lambda's readme.
