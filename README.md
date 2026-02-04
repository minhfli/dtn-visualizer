# custom DTN visualizer 
This is a visualizer I made for my graduation research project with ns3, UAV ferry network, DTN

## What is it

NetAnim is hard to understand and customize so I wrote something new

example trace file: ferry.log, test.log

## Trace file explained

Trace/log file contain 2 part: Declare and Event

Events are organized into timeframes, in one timeframe, there can be multiple events

some event are:
- pos: position update
- beacon: beacon broadcast
- send: packet send
- buffer: buffer update
- route: route update

## Credit

Thanks ChatGPT :>
