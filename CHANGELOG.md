# Changelog

## [0.11.0](https://github.com/scop/pytekukko/compare/v0.10.0...v0.11.0) (2022-03-26)


### Features

* **models:** expose CustomerData.name ([c835fea](https://github.com/scop/pytekukko/commit/c835fea47a580c38f2eeb3d070369b98e57a7854))

## [0.10.0](https://www.github.com/scop/pytekukko/compare/v0.9.0...v0.10.0) (2021-12-06)


### Features

* **examples:** load env from $PYTEKUKKO_DOTENV, actually walk from cwd ([9ac3df4](https://www.github.com/scop/pytekukko/commit/9ac3df45d14ebd25b0037debb7070b08a6b4889a))


### Documentation

* **readme:** elaborate disclaimer a bit ([f0e87b1](https://www.github.com/scop/pytekukko/commit/f0e87b16737d1cbbcf25dc7e527223ed87921261))

## 0.9.0 (2021-12-06)


### Features

* **examples:** add collection schedule printer ([75d7e0a](https://www.github.com/scop/pytekukko/commit/75d7e0a10f6b9589ca093d2e0354c1b541df59ee))
* **examples:** add invoice header example ([fe62a74](https://www.github.com/scop/pytekukko/commit/fe62a748d3ac219460f1e146762fca6b169cc0c2))
* **examples:** output JSON from print_next_collection_dates ([8d7f7e8](https://www.github.com/scop/pytekukko/commit/8d7f7e83325db0bf74302bcb0d0c2ab45363e3a4))
* first somewhat complete version ([b5fa4d9](https://www.github.com/scop/pytekukko/commit/b5fa4d9105044f9159e9b6b517a3dc52575cd523))
* **models:** add InvoiceHeader name, due_date and total ([24ab20e](https://www.github.com/scop/pytekukko/commit/24ab20e87ed5f81ee18b414f52319ce9631f3113))
* **retry:** improve login loop exception ([b0f66fb](https://www.github.com/scop/pytekukko/commit/b0f66fb98ff9d01a5607792cc756fe563e0796b9))


### Bug Fixes

* **collection_schedule:** trigger login on HTTP bad request too ([8b196fd](https://www.github.com/scop/pytekukko/commit/8b196fd5a4b411ec1ac349fc04c39fefb68daea3))
* **get_collection_schedule:** auto re-login on internal server error ([2540feb](https://www.github.com/scop/pytekukko/commit/2540feb2b535d0595f317e82bf1a0a599b936da6))
* **models:** remove InvoiceHeader.customer_number ([f52345e](https://www.github.com/scop/pytekukko/commit/f52345e191d0ff95b150e844936fc9b474fbd45d))


### Miscellaneous Chores

* release next as 0.9.0 ([36ab8eb](https://www.github.com/scop/pytekukko/commit/36ab8ebfc9325f25146c1402ed555a6f7c811a78))


### Documentation

* **examples:** add required Google Calendar data notes ([b3df6dc](https://www.github.com/scop/pytekukko/commit/b3df6dcec13ce4448680003ffdb24f2f3bf756e4))
* **examples:** note .env loading in --help output ([b77e3f4](https://www.github.com/scop/pytekukko/commit/b77e3f4ce7a7a14e69191a40c7ed82d721a3c969))
* improve and be consistent with project description ([1f64578](https://www.github.com/scop/pytekukko/commit/1f6457834755989e3eac855e5739778d4bfe2145))
* **readme:** add disclaimer ([2aaf32c](https://www.github.com/scop/pytekukko/commit/2aaf32c33d3fcb855524183760314e9ed2662222))
* **readme:** clarify what API uses cookies ([7c5e1d2](https://www.github.com/scop/pytekukko/commit/7c5e1d27905cb3f31357cdad99408d8b3636dc2f))
* **readme:** elaborate on design and goals a bit ([6791b76](https://www.github.com/scop/pytekukko/commit/6791b76cfaee3a499b9021337f98edb257715ae5))
* **readme:** initial write up ([fb7588a](https://www.github.com/scop/pytekukko/commit/fb7588aa0a52f7c8c5464bcbeece7ae1a46adfc3))
* **readme:** link to aiohttp objects ([4eea46a](https://www.github.com/scop/pytekukko/commit/4eea46ac44e1afa7257f3ad38de4c4d6caf32844))
* **readme:** run through prettier ([157ed3b](https://www.github.com/scop/pytekukko/commit/157ed3b51bc874936e9588a17ee6ad20153595eb))
* **readme:** wording tweaks ([2d01861](https://www.github.com/scop/pytekukko/commit/2d01861a01faabef758ec102e19b5670f2665b42))
* **requirements-test:** comment grammar fix ([2b91980](https://www.github.com/scop/pytekukko/commit/2b91980bd9c1642b1fcbab0cca778ebc10dc8375))
* spelling and grammar fixes ([4bf6eb9](https://www.github.com/scop/pytekukko/commit/4bf6eb9207d9f0ddfdf12a482ea4066882a64537))
* **version:** docstring copy-pasto fix ([4f0207e](https://www.github.com/scop/pytekukko/commit/4f0207ec417b47e5ba55898653bd3e1085e036d8))
