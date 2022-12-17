# Homework 4 - CI/CD

Before starting, make sure you have access to your AWS secret access key and access key ID from Homework 3.

## Intro

As you continue development on Aang's bender catalog, you realize that the steps for any developer to deploy the application are pretty arduous. To deploy any change, you have to:

- Build your docker images
- Find a new tag and tag the images with it
- Push up those images to your container registry
- Modify your Helm `values.yaml` to use the new image tag
- `helm upgrade --install` to actually update the release in the cluster

All of these tasks are auxiliary to the developer's main goal of getting to write code for new features, but they're required steps since we haven't automated them out of our workflow. In this lab, we'll use Continuous Integration and Continuous Delivery techniques to automate these steps out!

### Github Actions

For our Continuous Integration provider for this class, we've chosen [Github Actions](https://docs.github.com/en/actions). Github Actions has all the modern CI features we need, and more importantly, it integrates seamlessly with Github's [Container Registry](https://docs.github.com/en/packages/guides/about-github-container-registry) and parts of the Github ecosystem. This will make it easy to build our CI pipeline with as little extra configuration as possible.

## How to approach to this lab
Like we've stressed throughout the semester, learning how to sift through documentation is just as important a skill as learning the concepts behind Kubernetes specifically. For this lab, you'll be mostly on your own when it comes to resources and documentation. Remember, the [official docs](https://docs.github.com/en/actions) and Google are your friends here!

## File Structure

- `web/` - Holds the code and Dockerfile for our FastAPI application. You'll use this to build your `unit4-fastapi` image on push.
- `cronjob/` - Holds the code and Dockerfile for our cronjob. You'll use this to build your `unit4-cronjob` image on push.
- `.github/workflows/build-and-deploy.yml` - Our CI config file. You'll use this to configure Github Actions.

### Custom Installation Values

The `bender-catalog` chart is meant to be generalized to the whole class, but since you'll be deploying to a namespace based on your Pennkey, there will be differences in values between students. Before starting the assignment, modify `installation-values.yaml` to fit your Pennkey.

## Testing

Before we deploy, we need to make sure our code actually works! We've written a few tests in `web/`. To run them, `poetry install` in the directory, and then run `poetry run pytest`. You should see 3 tests being run and passing.

Your first job is to modify the `test` job in the Actions config we've provided you to test out your application! At a high level, this step should:

- Install Poetry
	- This can be done through `pip3` or an action from the Github Marketplace
- Install all dependencies for `web`
- Run the tests for `web`

Once you've got this step working, add 3 more tests of your own to help validate the code.

## Building and Publishing

The next step in automating our deploy process is automating our Docker tasks, specifically building and publishing both of our images. In the Actions config we've provided you, there is a `build` job that currently only checks out the code. It's your job to write a series of steps that will:

- Log into docker for the registry `ghcr.io` (Github Container Registry)
	- The username you should use for `ghcr.io` is `${{ github.actor }}`, and the password is `${{ secrets.GITHUB_TOKEN }}`. Github sets up these variables automatically for us so we can use them as credentials for Github-related services.
- Build both images.
- Publish the images under their respective tags.
	- `ghcr.io/cis188/hw4-PENNKEY/unit4-fastapi:SHA_OF_CURRENT_COMMIT`
	- `ghcr.io/cis188/hw4-PENNKEY/unit4-cronjob:SHA_OF_CURRENT_COMMIT`
	- Where `SHA_OF_CURRENT_COMMIT` would change to be the actual git sha of the commit that the image was based on.

The official [Docker action](https://github.com/marketplace/actions/build-and-push-docker-images) will come in handy here.

You have to tag the published images with the SHA of our current commit so that you know what image tag to use in your deploy step. There are other options we could choose here: manual version tags, autoincrementing keys, etc, but they require more configuration to set up. Git SHA is convenient because we know it uniquely identifies the commit our CI is running on, and GitHub Actions provides it as a built-in environment variable.

It's also important that this step only execute if the tests pass!

Once you see your images being published successfully, continue to the deploy step.

## Deploying

Before starting to deploy your code, create two secrets on your repository. You can edit secrets by going to `Settings -> Secrets` on your repo. You'll want to generate a new set of credentials for GitHub actions to use. That way you can independently disable those credentials in case one set gets compromised. Follow the instructions in hw3 to generate that second set of credentials.

- `AWS_ACCESS_KEY_ID` - your new access key ID
- `AWS_SECRET_ACCESS_KEY` - your new secret access key

Use these in your CI job to authenticate into AWS.

Our next (and final) step is to actually deploy our code to Kubernetes. This should go in the `deploy` job that we've provided. At a high level, you should add these steps:
- Log into AWS.
	- The [AWS Credential Action](https://github.com/aws-actions/configure-aws-credentials) will be useful here.
- Get a kubeconfig from AWS.
	- Remember how this is done from the last lab!
- Install your chart into the cluster with the `cronjob` and `fastapi` image tags set to the SHA of the current commit. Make sure to use `installation-values.yaml`!
  - You should use the bender-catalog helm chart that we provide. It's available at https://helm.cis188.org and is called `bender-catalog`. You should check the [Helm docs](https://helm.sh/docs/) in order to determine how to use a remote chart (rather than one stored on your laptop like the last homework assignment)

This step should only run if the build stage succeeds!

Once the deploy step has finished, test out your live URL the same way you have in past homeworks. If the API responds as you expect it to, continue on to the last part of the homework.

## Branch Conditionals

Before moving on, test something out - make a small change to our README, branch out, and make a pull request to your repository. If you watch Github Actions, it will go through the full pipeline: test, build, deploy. As you may imagine, though, we don't want deploys to happen on pull requests or any non-master branches for that matter.

The last step of this homework is to modify your `build` and `deploy` steps such that `deploy` only executes when there is a merge into master or a push to master and `build` will build on all branches, but only publish to GitHub's registry when there is a merge into master or a push to master. This means that our code will only get deployed off master, not any pull requests.

If this is working properly, you should be able to commit up to your PR and not see any builds or deploys, but when you merge into master, you should see build and deploy jobs.

## Wait is that it?

Congratulations! You've built a fully-automated, devops-friendly deploy pipeline! Your code can now be deployed without any intervention from Sysadmins or SREs, and you can have trust in the code because of the tests you've written.

Over the past few weeks, you've worked up from a simple FastAPI application you could only run on your local machine to a scalable, automated pipeline that will allow you to quickly deliver new features with confidence. This is no small job, so give yourself a pat on the back.

## Submitting

To submit your homework assignment, just run `make zip` in this repository and upload the resulting zip to Gradescope.

<!-- Copyright CIS 188: Armaan Tobaccowalla & Peyton Walters -->
<!-- 8wMNcOiv45lLUk6AzCKkaL9nLrP9Grkd -->
