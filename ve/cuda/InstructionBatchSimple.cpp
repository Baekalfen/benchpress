/*
 * Copyright 2011 Troels Blum <troels@blum.dk>
 *
 * This file is part of cphVB <http://code.google.com/p/cphvb/>.
 *
 * cphVB is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * cphVB is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with cphVB. If not, see <http://www.gnu.org/licenses/>.
 */

#include <iostream>
#include <cphvb.h>
#include "InstructionBatchSimple.hpp"

InstructionBatchSimple::InstructionBatchSimple(Threads threads_, 
                                        DataManager* dataManager_,
                                        KernelGenerator* kernelGenerator_) :
    threads(threads_),
    dataManager(dataManager_),
    kernelGenerator(kernelGenerator_) 
{
#ifdef DEBUG
    std::cout << "[VE CUDA] Created InstructionBatch(" << this << ") with " << 
        threads << " threads." << std::endl;
#endif
}


void InstructionBatchSimple::add(cphVBinstruction* inst)
{
#ifdef DEBUG
    std::cout << "[VE CUDA] InstructionBatchSimple(" << this << ")::add(" << 
        *inst << ")" << std::endl;
#endif
    int nops = cphvb_operands(inst->opcode);
    dataManager->lock(inst->operand, nops, this);
#ifdef DEBUG
    std::cout << "[VE CUDA] InstructionBatchSimple(" << this << ")::add(" << 
        inst << ") : Queued" << std::endl;
#endif
    batch.push_back(inst);
}

void InstructionBatchSimple::execute()
{
#ifdef DEBUG
    std::cout << "[VE CUDA] Executing InstructionBatch with " << batch.size() 
              << " instructions: " << std::endl;
#endif
    if (batch.begin() != batch.end())
    {
#ifdef DEBUG
        InstructionIterator it;
        for (it = batch.begin() ;it != batch.end(); ++it)
        {
            std::cout << "[VE CUDA] \t" << **it << std::endl;
        }
#endif
        kernelGenerator->run(threads, batch.begin(), batch.end());
        batch.clear();
    }
}
