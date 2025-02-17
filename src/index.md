# Visualizing Intertextuality

A project to visualize intertexts in Latin poetry using [nodegoat](https://nodegoat.net/), [Observable Framework](https://observablehq.com/framework/), and Python.

```js
const nodegoatModel = FileAttachment("data/nodegoat_data.json").json()
```

```js
nodegoatModel
```

```js
const csvSamp = FileAttachment("data/sample_csv_loader.csv").csv({typed: true})
```

```js
Inputs.table(csvSamp)
```