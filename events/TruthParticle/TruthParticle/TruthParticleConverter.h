#ifndef TruthParticleConverter_h
#define TruthParticleConverter_h

#include "TruthParticle/TruthParticle.h"
#include "GaugiKernel/DataHandle.h"


namespace xAOD{

    struct TruthParticle_t{
        int pdgid;
        int seedid;
        float e;
        float et;
        float eta;
        float phi;
        float px;
        float py;
        float pz;
        float vx; // vertex position x (prod_vx)
        float vy; // vertex position y
        float vz; // vertex position z
    };

 
    class TruthParticleConverter{

        public:
            TruthParticleConverter()=default;
            ~TruthParticleConverter()=default;

            bool serialize(  std::string &, SG::EventContext &/*ctx*/, TTree *) const;
            bool deserialize( std::string &, int &, TTree *, SG::EventContext &/*ctx*/) const;
            bool convert(const TruthParticle *truth, TruthParticle_t &truth_t ) const;
            bool convert(const TruthParticle_t & , TruthParticle *&) const;
    };
}
#endif


