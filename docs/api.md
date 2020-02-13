# API Reference

This section of the documentation provides detailed information on functions, classes, and methods.

### Server Communication

Communicating with the NLP server ([`processors-server`](https://github.com/clu-ling/processors-server)) is handled by the following classes:

## `ProcessorsBaseAPI`

```eval_rst
.. autoclass:: processors.api.ProcessorsBaseAPI
    :show-inheritance:
```

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

### `OdinAPI`

```eval_rst
.. autoclass:: processors.api.OpenIEAPI
    :show-inheritance:
```

### `SentimentAnalysisAPI`

```eval_rst
.. autoclass:: processors.sentiment.SentimentAnalysisAPI
    :show-inheritance:
```

## Data Structures

### `NLPDatum`

```eval_rst
.. autoclass:: processors.ds.NLPDatum
    :show-inheritance:
```

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

### `Edge`

```eval_rst
.. autoclass:: processors.ds.Edge
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

## Annotators (Processors)

Text annotation is performed by communicating with one of the following annotators ("processors").

### `CluProcessor`

```eval_rst
.. autoclass:: processors.annotators.CluProcessor
    :show-inheritance:
```

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

### `SentimentAnalyzer`

```eval_rst
.. autoclass:: processors.sentiment.SentimentAnalyzer
    :show-inheritance:
```

### `CoreNLPSentimentAnalyzer`

```eval_rst
.. autoclass:: processors.sentiment.CoreNLPSentimentAnalyzer
    :show-inheritance:
```

## `paths`

### `DependencyUtils`

```eval_rst
.. autoclass:: processors.paths.DependencyUtils
    :show-inheritance:
```

### `HeadFinder`

```eval_rst
.. autoclass:: processors.paths.HeadFinder
    :show-inheritance:
```

## Serialization

### `JSONSerializer`

```eval_rst
.. autoclass:: processors.serialization.JSONSerializer
    :show-inheritance:
```

## Visualization

### `JupyterVisualizer`

.. autoclass:: processors.Visualization.JupyterVisualizer
    :show-inheritance:
```
