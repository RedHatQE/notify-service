# Helm Chart Release

The notify-service Helm Chart repo is hosted on the repo github webpage:

https://RedHatQE.github.io/notify-service/

To generate new release and update the webpage repo, do the following steps.

## Helm package chart

Make sure you have Helm installed on your host, and enter the charts/ dir:

    $ cd chart/

Then update the version in:

    $ vim Chart.yaml

if plan to have a new release.

Update Redis dependency version:

    $ cd ../
    $ helm dependency update chart/
    $ git add $the_new_redis_pacakge_file
    $ git commit

And package new chart with:

    $ helm package chart/ --destination .deploy

Then the new package could be found under .deploy dir, e.g.:

    $ ll .deploy/              Thu 06 Jan 2022 11:02:48 AM EST
    total 144K
    -rw-r--r--. 1 waynesun waynesun 70K May 20  2021 notify-service-0.0.1.tgz
    -rw-r--r--. 1 waynesun waynesun 70K Jan  6 09:52 notify-service-0.0.2.tgz

## Upload package with Chart Release CLI (cr) to github repo

Make sure you have the `cr` CLI installed, check detail in:

https://github.com/helm/chart-releaser

Maker sure you have created a `~/.cr.yaml` file with your github token like:

    CH_TOKEN: $GH_TOKEN

Replace the GH_TOKEN value with real GH token.

Run upload command:

    $ cr upload -o RedHatQE -r notify-service -t $YOUR_TOKEN --config ~/.cr.yaml -p .deploy/

## Create Helm repo index

After the package have been uploaded, checkout to the github page branch gh-page:

    $ git checkout gh-page

Update index with:

    $ cr index -i ./index.yaml -p .deploy -o RedHatQE -r notify-service -c https://RedHatQE.github.io/notify-service

Then commit the change and push to the repo, now the helm chart repo should be updated.

## Check the release

Add the helm chart repo:

    $ helm repo add notify https://RedHatQE.github.io/notify-service/

Check the latest release on the project with:

    $ helm repo update notify
    $ helm search repo notify-service
