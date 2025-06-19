import abc


class AbstractService(abc.ABC):
    """Abstract service"""

    @abc.abstractmethod
    async def get(self, *args, **kwargs):
        """Get instance"""

    @abc.abstractmethod
    async def create(self, *args, **kwargs):
        """Create instance"""
