### Example on `WindowFn`

This example will NOT work on a laptop. The code shows how window functions work in Apache Beam and how to create a Beam pipeline with windows.

#### Description of the key point of the pipeline

This is how the pipeline looks like:

```python

with beam.Pipeline(options=pipeline_options) as p:
    (p
        | 'Read from Pub/Sub' >> beam.io.ReadFromPubSub(
            subscription=known_args.input_subscription)
        | 'Parse JSON' >> beam.Map(lambda x: json.loads(x))
        | 'Window into' >> beam.WindowInto(window.FixedWindows(60))
        | 'WithKeys' >> beam.Map(lambda element: (
            element['event_type'], element['value']))
        | 'Group by Key' >> beam.GroupByKey()
        | 'Compute Moving Average' >> beam.ParDo(ComputeMovingAverageFn())
        | 'Encode JSON' >> beam.Map(lambda x: json.dumps(x).encode('utf-8'))
        | 'WriteToText' >> beam.io.WriteToText(known_args.output)
        )
```

At this stage we'll be focusing on `'Window into' >> beam.WindowInto(window.FixedWindows(60))` step.
The `Window into` accumulate all the input events in a Window that lasts 60 seconds. For example, suppose we have three different events, A, B, and C. Each event carries a number of "items" from a store:
```
1, event A, items: 10
2, event A, items: 25
3, event A, items: 30
4, event B, items: 15
5, event C, items: 25
6, event A, items: 40
7, event B, items: 20
8, event A, items: 10
9, event C, items: 2
```
Suppose these events are coming in chronological order, so that the events 1-5 happens in a minute, following events 6-9.
The `Window into` will create, after the first minute, an object similar to:
```
window_1: { [1, event A, items: 10
             2, event A, items: 25
             3, event A, items: 30],
            [4, event B, items: 15],
            [5, event C, items: 25]}
```
and after the second passed minute, something like:
```
window_1: { [1, event A, items: 10
             2, event A, items: 25
             3, event A, items: 30],
            [4, event B, items: 15],
            [5, event C, items: 25]},
window_2: { [6, event A, items: 40
             8, event A, items: 10],
            [7, event B, items: 20],
            [9, event C, items: 2]}
```
From here we can clearly see how it easy then to retrieve AGGREGATE features for each window we have, namely for each minute of processing.

In the subsequent step, `Group by Key` we are then collecting each window chunk based on keys:
```
window_1: { [event A, items: [10,25,30]],
            [event B, items: [15]],
            [event C, items: [25]]},
window_2: { [event A, items: [40,10]],
            [event B, items: [20]],
            [event C, items: [2]]}
```

From here it is easy to see how to retrieve the averages for each single window.