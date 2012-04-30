/* Copyright (c) 2009 maidsafe.net limited
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
    this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation
    and/or other materials provided with the distribution.
    * Neither the name of the maidsafe.net limited nor the names of its
    contributors may be used to endorse or promote products derived from this
    software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#include "maidsafe/dht/contact.h"

#include <string>
#ifdef __MSVC__
#  pragma warning(push)
#  pragma warning(disable: 4127 4244 4267)
#endif
#include "maidsafe/dht/kademlia.pb.h"
#ifdef __MSVC__
#  pragma warning(pop)
#endif
#include "maidsafe/dht/log.h"
#include "maidsafe/dht/utils.h"

namespace maidsafe {

namespace dht {

Contact::Contact()
    : node_id_(),
      public_key_id_(),
      public_key_(),
      other_info_(),
      transport_details_() {}

Contact::Contact(const Contact &other)
    : node_id_(other.node_id_),
      public_key_id_(other.public_key_id_),
      public_key_(other.public_key_),
      other_info_(other.other_info_),
      transport_details_(other.transport_details_) {}

Contact::Contact(const NodeId &node_id,
                 const transport::Endpoint &endpoint,
                 const std::vector<transport::Endpoint> &local_endpoints,
                 const transport::Endpoint &rendezvous_endpoint,
                 bool tcp443,
                 bool tcp80,
                 const asymm::Identity &public_key_id,
                 const asymm::PublicKey &public_key,
                 const std::string &other_info)
    : node_id_(node_id),
      public_key_id_(public_key_id),
      public_key_(public_key),
      other_info_(other_info),
      transport_details_(transport::Contact(endpoint, local_endpoints,
                                            rendezvous_endpoint, tcp443,
                                            tcp80)) {
  Init();
}

void Contact::Init() {
  if (!node_id_.IsValid() || !transport_details_.Init())
    return Clear();
}

void Contact::Clear() {
  transport_details_.Clear();
  node_id_ = NodeId();
}

Contact::~Contact() {}

NodeId Contact::node_id() const {
  return node_id_;
}

asymm::Identity Contact::public_key_id() const {
    return public_key_id_;
}

asymm::PublicKey Contact::public_key() const {
  return public_key_;
}

std::string Contact::other_info() const {
  return other_info_;
}

transport::Endpoint Contact::endpoint() const {
  return transport_details_.endpoint();
}

std::vector<transport::Endpoint> Contact::local_endpoints() const {
  return transport_details_.local_endpoints();
}

transport::Endpoint Contact::rendezvous_endpoint() const {
  return transport_details_.rendezvous_endpoint();
}

transport::Endpoint Contact::tcp443endpoint() const {
  return transport_details_.tcp443endpoint();
}

transport::Endpoint Contact::tcp80endpoint() const {
  return transport_details_.tcp80endpoint();
}

bool Contact::SetPreferredEndpoint(const transport::IP &ip) {
  return transport_details_.SetPreferredEndpoint(ip);
}

bool Contact::MoveLocalEndpointToFirst(const transport::IP &ip) {
  return transport_details_.MoveLocalEndpointToFirst(ip);
}

bool Contact::IpMatchesEndpoint(const transport::IP &ip,
                                const transport::Endpoint &endpoint) {
  return transport_details_.IpMatchesEndpoint(ip, endpoint);
}

transport::Endpoint Contact::PreferredEndpoint() const {
  return transport_details_.PreferredEndpoint();
}

bool Contact::IsDirectlyConnected() const {
  return transport_details_.IsDirectlyConnected();
}

int Contact::Serialise(std::string * serialised) const {
  protobuf::Contact pb_contact;
  boost::system::error_code ec;

  protobuf::Endpoint *mutable_endpoint = pb_contact.mutable_endpoint();
  mutable_endpoint->set_ip(endpoint().ip.to_string(ec));
  mutable_endpoint->set_port(endpoint().port);

  if (IsValid(rendezvous_endpoint())) {
    mutable_endpoint = pb_contact.mutable_rendezvous();
    mutable_endpoint->set_ip(rendezvous_endpoint().ip.to_string(ec));
    mutable_endpoint->set_port(rendezvous_endpoint().port);
  }

  std::vector<transport::Endpoint> local_ep_vector(local_endpoints());
  for (auto it = local_ep_vector.begin(); it != local_ep_vector.end(); ++it) {
    pb_contact.add_local_ips((*it).ip.to_string(ec));
    pb_contact.set_local_port((*it).port);
  }
  if (IsValid(tcp443endpoint()))
    pb_contact.set_tcp443(true);
  if (IsValid(tcp80endpoint()))
    pb_contact.set_tcp80(true);
  // TODO(Prakash): FIXME
  if ((PreferredEndpoint().ip == rendezvous_endpoint().ip) ||
      (PreferredEndpoint().ip == endpoint().ip))
    pb_contact.set_prefer_local(false);
  else
    pb_contact.set_prefer_local(true);

  pb_contact.set_node_id(node_id().String());
  pb_contact.set_public_key_id(public_key_id());
  std::string encode_pub_key;
  asymm::EncodePublicKey(public_key(), &encode_pub_key);
  pb_contact.set_public_key(encode_pub_key);
  pb_contact.set_other_info(other_info());

  if (!pb_contact.IsInitialized())
    return kSerialisation;

  if (!pb_contact.SerializeToString(serialised)) {
    return kSerialisation;
  }
  return kSuccess;
}

int Contact::Parse(const std::string & serialised) {
  protobuf::Contact pb_contact;
  if (!pb_contact.ParseFromString(serialised)) {
    Clear();
    return kParse;
  }
  if (transport_details_.Parse(serialised) != kSuccess) {
    Clear();
    return kParse;
  }
  node_id_ = NodeId(pb_contact.node_id());

  public_key_id_ =
      pb_contact.has_public_key_id() ? pb_contact.public_key_id() : "";

  asymm::PublicKey public_key;
  if (pb_contact.has_public_key())
    asymm::DecodePublicKey(pb_contact.public_key(), &public_key);
  public_key_ = public_key;

  other_info_ =
      pb_contact.has_other_info() ? pb_contact.other_info() : "";

  return kSuccess;
}

Contact& Contact::operator=(const Contact &other) {
  if (this != &other) {
    node_id_ = other.node_id_;
    public_key_id_ = other.public_key_id_;
    public_key_ = other.public_key_;
    other_info_ = other.other_info_;
    transport_details_ = other.transport_details_;
  }
  return *this;
}

bool Contact::operator==(const Contact &other) const {
  if (node_id_ == other.node_id_)
    return (node_id_.String() != kZeroId) ||
           (endpoint().ip == other.endpoint().ip);
  else
    return false;
}

bool Contact::operator!=(const Contact &other) const {
  return !(*this == other);
}

bool Contact::operator<(const Contact &other) const {
  return node_id_ < other.node_id_;
}

bool Contact::operator>(const Contact &other) const {
  return node_id_ > other.node_id_;
}

bool Contact::operator<=(const Contact &other) const {
  return (node_id_ < other.node_id_ || (*this == other));
}

bool Contact::operator>=(const Contact &other) const {
  return (node_id_ > other.node_id_ || (*this == other));
}

std::string DebugId(const Contact &contact) {
  return DebugId(contact.node_id());
}

bool CloserToTarget(const NodeId &node_id,
                    const Contact &contact,
                    const NodeId &target) {
  return NodeId::CloserToTarget(node_id, contact.node_id(), target);
}

bool CloserToTarget(const Contact &contact1,
                    const Contact &contact2,
                    const NodeId &target) {
  return NodeId::CloserToTarget(contact1.node_id(), contact2.node_id(), target);
}

bool NodeWithinClosest(const NodeId &node_id,
                       const std::vector<Contact> &closest_contacts,
                       const NodeId &target) {
  return std::find_if(closest_contacts.rbegin(), closest_contacts.rend(),
      std::bind(static_cast<bool(*)(const NodeId&,  // NOLINT
                                    const Contact&,
                                    const NodeId&)>(&CloserToTarget),
                node_id, args::_1, target)) != closest_contacts.rend();
}

bool RemoveContact(const NodeId &node_id, std::vector<Contact> *contacts) {
  if (!contacts)
    return false;
  size_t size_before(contacts->size());
  contacts->erase(std::remove_if(contacts->begin(), contacts->end(),
                                 std::bind(&HasId, args::_1, node_id)),
                  contacts->end());
  return contacts->size() != size_before;
}

bool WriteContactsToFile(const fs::path &filename,
                         std::vector<Contact> *contacts) {
  if (contacts == nullptr)
    return false;
  protobuf::BootstrapContacts bootstrap_contacts;
  for (size_t i = 0; i < contacts->size(); i++) {
    protobuf::Contact * pb_contact = bootstrap_contacts.add_contact();
    *pb_contact = ToProtobuf(contacts->at(i));
  }
  {
    // Write the new bootstrap contacts back to disk.
    std::ofstream ofs(filename.c_str(), std::ios::binary | std::ios::trunc);
    if (!bootstrap_contacts.SerializeToOstream(&ofs)) {
      DLOG(WARNING) << "Failed to write bootstrap contacts.";
      return false;
    }
  }
  return true;
}

bool ReadContactsFromFile(const fs::path &filename,
                          std::vector<Contact> *contacts) {
  if (contacts == nullptr)
    return false;
  protobuf::BootstrapContacts bootstrap_contacts;
  {
    // Read the existing bootstrap contacts.
    std::ifstream ifs(filename.c_str(), std::ios::binary);
    if (!ifs.is_open()) {
      DLOG(WARNING) << "Failed to open file : " <<  filename.string();
      return false;
    }
    if (!bootstrap_contacts.ParseFromIstream(&ifs)) {
      DLOG(WARNING) << "Failed to parse bootstrap contacts.";
      return false;
    }
  }
  for (int i = 0; i < bootstrap_contacts.contact_size(); i++) {
    Contact contact = FromProtobuf(bootstrap_contacts.contact(i));
    contacts->push_back(contact);
  }
  return true;
}

}  // namespace dht

}  // namespace maidsafe
