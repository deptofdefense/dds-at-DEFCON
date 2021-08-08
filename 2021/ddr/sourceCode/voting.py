# script to handle voting for rover ground station

class Voter:
    """
    Class that represents an individual voter
    """
    
    def __init__(self, name, vote):
        """
        Init method

        Args:
            name (str): the voter name
            vote (str): the voters vote
        """
        self.name = name
        self.vote = vote
        
    def __eq__(self, o: object):
        
        if (isinstance(o, self.__class__) and getattr(o, 'name', None) == self.name): # check if class and name match
            
            if o.vote != self.vote: # vote has changed
                self.vote = o.vote # update vote
                #print("updated in eq")
            return True
        else:
            return False
                
    def __hash__(self):
        return hash(str(self.name))
    
    def updateVote(self, vote):
        """
        Updates the current voters vote

        Args:
            vote (str): the new vote
        """
        
        self.vote = vote
        
class VoteTracker:
        """
        Keeps track of all voters and announces winner
        """
        
        def __init__(self):
            self.voterList = set()
            
        def addVoter(self, name, vote):
            """
            Checks if a voter is in the list and either adds them or updates their vote

            Args:
                name (str): the name of the voter
                vote (vote): the voters vote
            """
            
            newVoter = Voter(name, vote)
            
            self.voterList.add(newVoter)
            
        def reset(self):
            """
            resets the vote tracker
            """
            self.voterList = set()
            
        def countVotes(self):
            
            fwd = 0
            bwd = 0
            lft = 0
            rgt = 0

            for voter in self.voterList:
                if voter.vote == "fwd":
                    fwd = fwd + 1
                elif voter.vote == "lft":
                    lft = lft + 1
                elif voter.vote == "rgt":
                    rgt = rgt + 1
                else:
                    bwd = bwd + 1
                    
            if fwd >= lft and fwd >= rgt and fwd >= bwd:
                return "fwd"
            elif lft >= fwd and lft >= rgt and lft >= bwd:
                return "lft"
            elif rgt >= fwd and rgt >= lft and rgt >= bwd:
                return "rgt"
            else:
                return "bwd"

        def printVotes(self):

            fwd = 0
            bwd = 0
            lft = 0
            rgt = 0

            for voter in self.voterList:
                if voter.vote == "fwd":
                    fwd = fwd + 1
                elif voter.vote == "lft":
                    lft = lft + 1
                elif voter.vote == "rgt":
                    rgt = rgt + 1
                else:
                    bwd = bwd + 1

            return f"forward: {str(fwd)}\nleft: {str(lft)}\nbackward: {str(bwd)}\nright: {str(rgt)}\n"
    
    
if __name__ == "__main__":

    voteTrack = VoteTracker()
    
    voteTrack.addVoter("a", "lft")
    voteTrack.addVoter("a", "rgt")
    voteTrack.addVoter("b", "rgt")
    voteTrack.addVoter("c", "bwd")
    voteTrack.addVoter("d", "fwd")
    
    result = voteTrack.countVotes()
    
    print(str(result))