# API Reference

This section of the documentation provides detailed information on functions, classes, and methods.

### Server Communication

Communicating with the NLP server ([`processors-server`](https://github.com/myedibleenso/processors-server)) is handled by the following classes.

## `ProcessorsAPI`

```eval_rst
.. autoclass:: processors.api.ProcessorsAPI
    :show-inheritance:
```

### `OdinAPI`

```eval_rst
.. autoclass:: processors.api.OdinAPI
    :show-inheritance:
```

### `SentimentAnalysisAPI`

```eval_rst
.. autoclass:: processors.sentiment.SentimentAnalysisAPI
    :show-inheritance:
```

## Data Structures

### `Document`

```eval_rst
.. autoclass:: processors.ds.Document
    :show-inheritance:
```

### `Sentence`

```eval_rst
.. autoclass:: processors.ds.Sentence
    :show-inheritance:
```

### `DirectedGraph`

```eval_rst
.. autoclass:: processors.ds.DirectedGraph
    :show-inheritance:
```

### `Mention`

```eval_rst
.. autoclass:: processors.odin.Mention
    :show-inheritance:
```

`JSON` serialization/deserialization is handled via `processors.serialization.JSONSerializer`.

### `Interval`

```eval_rst
.. autoclass:: processors.ds.Interval
    :show-inheritance:
```

## DependencyUtils
```eval_rst
.. autoclass:: processors.paths.DependencyUtils
    :show-inheritance:
```

## Annotators (Processors)

Text annotation is performed by communicating with one of the following annotators ("processors").  

### `FastNLPProcessor`

```eval_rst
.. autoclass:: processors.annotators.FastNLPProcessor
    :show-inheritance:
```

### `BioNLPProcessor`

```eval_rst
.. autoclass:: processors.annotators.BioNLPProcessor
    :show-inheritance:
```

## Sentiment Analysis

```eval_rst
.. autoclass:: processors.sentiment.BioNLPProcessor
    :show-inheritance:
```

## Serialization

```eval_rst
.. autoclass:: processors.serialization.JSONSerializer
    :show-inheritance:
```
