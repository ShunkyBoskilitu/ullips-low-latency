/* p4_switch_matcher.p4: P4-16 In-Network LOB Imbalance Filter for P4 Programmable Switches */

#include <core.p4>
#include <v1model.p4>

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header order_hdr_t {
    bit<32> security_id;
    bit<32> bid_volume;
    bit<32> ask_volume;
    bit<8>  signal_action; // 0: Neutral, 1: Buy, 2: Sell
}

struct metadata {
    bit<32> depth_diff;
    bit<32> depth_sum;
}

struct headers {
    ethernet_t ethernet;
    order_hdr_t order;
}

parser MyParser(packet_in packet, out headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            0x0800: parse_order;
            default: accept;
        }
    }
    state parse_order {
        packet.extract(hdr.order);
        transition accept;
    }
}

control MyIngress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    action compute_imbalance() {
        // Fast in-network fixed point comparison bypassing Linux socket stack
        if (hdr.order.bid_volume > (hdr.order.ask_volume << 2)) {
            hdr.order.signal_action = 1; // Heavy bid imbalance
        } else if (hdr.order.ask_volume > (hdr.order.bid_volume << 2)) {
            hdr.order.signal_action = 2; // Heavy ask imbalance
        }
    }
    table imbalance_filter {
        key = { hdr.order.security_id: exact; }
        actions = { compute_imbalance; NoAction; }
        default_action = NoAction;
    }
    apply {
        imbalance_filter.apply();
    }
}

control MyEgress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) { apply { } }
control MyDeparser(packet_out packet, in headers hdr) { apply { packet.emit(hdr.ethernet); packet.emit(hdr.order); } }
control MyVerifyChecksum(inout headers hdr, inout metadata meta) { apply { } }
control MyComputeChecksum(inout headers hdr, inout metadata meta) { apply { } }

V1Switch(MyParser(), MyVerifyChecksum(), MyIngress(), MyEgress(), MyComputeChecksum(), MyDeparser()) main;
