simple Source
{
    gates:
        output out;
}

simple Sink
{
    gates:
        input in;
}

network Clean
{
    submodules:
        source: Source;
        sink: Sink;
    connections:
        source.out --> sink.in;
}
